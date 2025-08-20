# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/23
# @File : api.py
import asyncio
import datetime
import time

import pytz
from common.settings import REDIS_CONFIG
from fastapi import APIRouter, HTTPException
from .schemas import CornJobFrom, UpdagteCornJobFrom
from apps.Crontab.models import CronJob
from apps.TestTask.models import TestTask
from apps.projects.models import Env, Project
from tortoise import transactions
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.redis import RedisJobStore

from ..TestTask.api import run_task
from ..TestTask.schemas import RunTaskForm

router = APIRouter(prefix='/api/crontab')
local_timezone = pytz.timezone('Asia/Shanghai')

# 配置 APScheduler
job_stores = {
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

scheduler = AsyncIOScheduler(jobstores=job_stores, job_defaults=job_defaults,
                             timezone='Asia/Shanghai')


# scheduler.start()


# ==================================APS ==================================


async def init_scheduler():
    global scheduler
    scheduler = AsyncIOScheduler(jobstores=job_stores, job_defaults=job_defaults, timezone='Asia/Shanghai')
    scheduler.start()


async def run_test_task(task_id, env_id, tester):
    """执行定时任务"""
    print("任务执行提交", datetime.datetime.now(), task_id, env_id)
    try:
        print(f"准备执行任务: task_id={task_id}, env_id={env_id}, tester={tester}")
        async with transactions.in_transaction() as conn:
            print("开始执行 run_task")
            # 添加超时控制，比如设置30秒超时
            try:
                result = await asyncio.wait_for(
                    run_task(RunTaskForm(env=env_id, task=task_id, tester=tester)),
                    timeout=30.0
                )
                print("run_task 执行完成，返回结果:", result)
            except asyncio.TimeoutError:
                print("run_task 执行超时")
                raise
        print("定时任务执行了", task_id, env_id, datetime.datetime.now())
        return result
    except Exception as e:
        error_msg = f"定时任务执行失败: task_id={task_id}, env_id={env_id}, tester={tester}, 错误: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()



# 创建测试任务
@router.post('/cronjob', tags=['定时任务'], summary="创建定时任务", status_code=201)
async def create_crontab(item: CornJobFrom):
    # corn_task_id = str(int(time.time() * 1000))

    task = await TestTask.get_or_none(id=item.task)
    if not task:
        raise HTTPException(status_code=422, detail='创建失败,测试任务不存在')

    env = await Env.get_or_none(id=item.env)
    if not env:
        raise HTTPException(status_code=422, detail='创建失败,执行环境不存在')

    project = await Project.get_or_none(id=item.project)
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

            corn = await CronJob.create(name=item.name, project_id=item.project, task_id=item.task,
                                        env_id=item.env, run_type=item.run_type, interval=item.interval,
                                        date=item.date, crontab=item.crontab.dict(), state=item.state)
            job = scheduler.add_job(
                func=run_test_task,
                trigger=trigger,
                id=str(corn.id),
                name=item.name,
                kwargs={"task_id": item.task, "env_id": item.env, "tester": item.tester}
            )
        except Exception as e:
            # 事务回滚
            await cron_tran.rollback()
            # 取消定时任务
            scheduler.remove_job(corn.id)
            raise HTTPException(status_code=422, detail=f'创建失败{e}')
        else:
            await cron_tran.commit()
            return corn


# 获取定时任务列表
@router.get('/cronjob', tags=['定时任务'], summary="获取定时任务列表")
async def get_crontab_list(project: int):
    res =  await CronJob.filter(project_id=project).all().prefetch_related('task', 'env')
    return [{
        "id": corn.id,
        "create_time":corn.create_time.astimezone(local_timezone).strftime('%Y-%m-%d %H:%M:%S'),
        "name": corn.name,
        "task": corn.task.name,
        "env": corn.env.name,
        "run_type": corn.run_type,
        "interval": corn.interval,
        "date": corn.date.strftime('%Y-%m-%d %H:%M:%S'),
        "crontab": corn.crontab,
        "state": corn.state
    } for corn in res]

# 暂停/恢复定时任务
@router.patch('/cronjob/{id}', tags=['定时任务'], summary="暂停/恢复定时任务")
async def update_crontab(id: str):
    corn = await CronJob.get_or_none(id=id)
    if not corn:
        raise HTTPException(status_code=422, detail='定时任务不存在')
    if scheduler.get_job(id):
        scheduler.pause_job(id)
    async with transactions.in_transaction() as cron_tran:
        try:
            corn.state = not corn.state
            # 判断是启用还是暂停
            if corn.state:
                scheduler.resume_job(id)
            else:
                scheduler.pause_job(id)
            await corn.save()
        except Exception as e:
            await cron_tran.rollback()
            raise HTTPException(status_code=422, detail='操作失败')
        else:
            await cron_tran.commit()
        return corn


# 删除定时任务
@router.delete('/cronjob/{id}', tags=['定时任务'], summary="删除定时任务", status_code=204)
async def delete_crontab(id: str):
    corn = await CronJob.get_or_none(id=id)
    if not corn:
        raise HTTPException(status_code=422, detail='定时任务不存在')
    if scheduler.get_job(id):
        scheduler.remove_job(id)
    await corn.delete()


# 修改定时任务配置
@router.put('/cronjob/{id}', tags=['定时任务'], summary="修改定时任务配置")
async def update_job(id: str, item: UpdagteCornJobFrom):
    corn = await CronJob.get_or_none(id=id)
    if not corn:
        raise HTTPException(status_code=422, detail='定时任务不存在')

    if item.run_type not in ['Interval', 'date', 'crontab']:
        raise HTTPException(status_code=422, detail='创建失败,任务类型错误')

    date = datetime.datetime.strptime(item.date, '%Y-%m-%d %H:%M:%S')
    if date < datetime.datetime.now() and item.run_type == 'date':
        raise HTTPException(status_code=422, detail='创建失败,执行时间不能小于当前时间')
    try:
        if corn.run_type == 'Interval':
            trigger = IntervalTrigger(seconds=item.interval, timezone=local_timezone)
        elif corn.run_type == 'date':
            trigger = DateTrigger(run_date=item.date, timezone=local_timezone)
        else:
            trigger = CronTrigger(**item.crontab.dict(), timezone=local_timezone)

        scheduler.modify_job(id, trigger=trigger)
        await corn.update_from_dict(item.dict(exclude_unset=True)).save()

    except Exception as e:
        raise HTTPException(status_code=422, detail=f'修改失败:{e}')

    return corn
