# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/23
# @File : api.py
import datetime
import time

import pytz
from fastapi import APIRouter
from common.rabbitmq_producer import mq
from common.settings import REDIS_CONFIG
from fastapi import APIRouter, HTTPException
from .schemas import CornJobFrom, UpdagteCornJobFrom
from apps.Crontab.models import CronJob
from apps.TestTask.models import TestTask, TestRecord
from apps.projects.models import Env, Project
from tortoise import transactions
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore

from ..Suite.models import Suite

router = APIRouter(prefix='/api/crontab')
local_timezone = pytz.timezone('Asia/Shanghai')

# 配置 APScheduler
jobstores = {
    'default': RedisJobStore(host=REDIS_CONFIG.get('host'),
                             port=REDIS_CONFIG.get('port'),
                             db=REDIS_CONFIG.get('db'),
                             password=REDIS_CONFIG.get('password'))
}
# 设置最大的执行线程数 （使用异步，不用线程）
# executors = {
#     'default': ThreadPoolExecutor(20)
# }
# 设置最大的任务数
job_defaults = {
    'coalesce': False,
    'max_instances': 10
}
# 创建一个调度器
# scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults,
#                                 timezone='Asia/Shanghai')

scheduler = AsyncIOScheduler(jobstores=jobstores, job_defaults=job_defaults,
                             timezone='Asia/Shanghai')

scheduler.start()


# ==================================APS ==================================


async def run_test_task(task_id, env_id):
    """执行定时任务"""
    async with transactions.in_transaction():
        task = await TestTask.get_or_none(id=task_id).prefetch_related('suite', 'project')
        env = await Env.get_or_none(id=env_id)
        env_config = {
            "is_debug": False,
            "browser_type": 'chromium',
            "host": env.host,
            "global_variable": env.global_vars
        }
        # 创建一条任务执行的记录
        task_record = await TestRecord.create(task=task, env=env_config, project=task.project)
        task_count = 0
        for suite in await task.suite.all():
            cases = []
            suite_ = await Suite.get_or_none(id=suite.id).prefetch_related('cases')
            suite_record = await SuiteRunRecords.create(suite=suite_, env=env_config, task_run_records=task_record)
            for i in await suite_.cases.all().order_by("sort"):
                case_ = await i.cases
                case_record = await CaseRunRecords.create(case=case_, suite_run_records=suite_record)
                cases.append({
                    "record_id": case_record.id,
                    'id': case_.id,
                    'name': case_.name,
                    'skip': i.skip,
                    'steps': case_.steps
                })
            task_count += len(cases)
            suite_record.all = len(cases)
            await suite_record.save()
            run_suite = {
                'id': suite_.id,
                "suite_record_id": suite_record.id,
                "task_record_id": task_record.id,
                'name': suite_.name,
                'setup_step': suite_.suite_setup_step,
                'cases': cases
            }
            mq.send_test_task(env_config, run_suite)

        # 修改任务中的用例总数
        task_record.all = task_count
        await task_record.save()
    print("任务执行提交", task_id, env_id)

    # print("执行了", task_id, env_id)


# 创建测试任务
@router.post('/crontab', tags=['定时任务'], summary="创建定时任务", status_code=201)
async def create_crontab(item: CornJobFrom):
    corn_task_id = str(int(time.time() * 1000))

    task = TestTask.get_or_none(id=item.task)
    if not task:
        raise HTTPException(status_code=422, detail='创建失败,测试任务不存在')

    env = Env.get_or_none(id=item.env)
    if not env:
        raise HTTPException(status_code=422, detail='创建失败,执行环境不存在')

    project = Project.get_or_none(id=item.project)
    if not project:
        raise HTTPException(status_code=422, detail='创建失败,所属项目不存在')

    if item.run_type not in ['Interval', 'date', 'crontab']:
        raise HTTPException(status_code=422, detail='创建失败,任务类型错误')

    date = datetime.datetime.strptime(item.date, '%Y-%m-%d %H:%M:%S')
    if date < datetime.datetime.now() and item.run_type == 'date':
        raise HTTPException(status_code=422, detail='创建失败,执行时间不能小于当前时间')

    # 添加事务
    async with transactions.in_transaction('default') as cron_tran:
        try:
            if item.run_type == 'Interval':
                trigger = IntervalTrigger(seconds=item.interval, timezone=local_timezone)
            elif item.run_type == 'date':
                trigger = DateTrigger(run_date=date, timezone=local_timezone)
            else:
                trigger = CronTrigger(**item.crontab.dict(), timezone=local_timezone)

            job = scheduler.add_job(
                func=run_test_task,
                trigger=trigger,
                id=corn_task_id,
                name=item.name,
                kwargs={"task_id": item.task, "env_id": item.env}
            )
            corn = await CronJob.create(id=corn_task_id, name=item.name, project_id=item.project, task_id=item.task,
                                        env_id=item.env, run_type=item.run_type, interval=item.interval,
                                        date=item.date, crontab=item.crontab.dict(), state=item.state)
        except Exception as e:
            # 事务回滚
            await cron_tran.rollback()
            # 取消定时任务
            scheduler.remove_job(corn_task_id)
            raise HTTPException(status_code=422, detail='创建失败')
        else:
            await cron_tran.commit()
            return corn
