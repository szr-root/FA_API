# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : api.py
import json
import time
from typing import Optional

from fastapi import APIRouter, HTTPException
from tortoise.transactions import in_transaction

from .models import TestTask, TestReport, TestRecord
from .schemas import AddTaskForm, RunTaskForm, UpdateTaskForm
from ..Suite.api import run_scenes
from ..Suite.models import Suite
from ..Suite.schemas import SuiteRunForm
from ..projects.models import Project

router = APIRouter(prefix="/api/TestTask", tags=["测试任务"])


# 创建测试任务
@router.post('/tasks', summary='创建测试任务', status_code=201)
async def create_task(item: AddTaskForm):
    project = await Project.get_or_none(id=item.project)
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")
    item.project = project
    # 获取所有套件
    suites = await Suite.filter(id__in=item.flow)
    if len(suites) != len(item.flow):
        raise HTTPException(status_code=422, detail="部分套件不存在")
        # 创建测试任务，排除多对多字段
    task_data = item.dict(exclude={'suite'})
    task = await TestTask.create(**task_data)
    # 关联套件
    await task.suite.add(*suites)

    return {"id": task.pk, "name": task.name, "flow": [flow.id for flow in suites]}


# 查询所有测试任务
@router.get('/tasks', summary='查询所有测试任务')
async def get_tasks(project: int):
    tasks = await TestTask.filter(project_id=project).prefetch_related('suite')
    return [{"id": task.pk, "name": task.name, "flow": [flow.id for flow in task.suite]} for task in tasks]


# 获取单个任务详情
@router.get('/tasks/{task_id}', summary='获取单个任务详情')
async def get_task(task_id: int):
    task = await TestTask.get_or_none(id=task_id).prefetch_related('suite')
    if not task:
        raise HTTPException(status_code=422, detail="任务不存在")
    data = {"id": task.pk, "name": task.name,
            "flow": [{
                "id": flow.id, "name": flow.name
            } for flow in task.suite]}
    return data


# 向测试任务中添加测试套件
@router.patch('/tasks/{task_id}', summary='向测试任务中添加测试套件')
async def add_icase(item: UpdateTaskForm):
    task = await TestTask.get_or_none(id=item.id).prefetch_related('suite')
    # 更新任务的基本信息
    task.name = item.name

    # 获取当前关联的套件ID集合
    current_suite_ids = {suite.id for suite in task.suite}
    new_suite_ids = set(item.flow)

    # 计算需要删除和添加的套件ID
    to_remove = current_suite_ids - new_suite_ids
    to_add = new_suite_ids - current_suite_ids

    # # 删除不再关联的套件
    for suite_id in to_remove:
        await task.suite.remove(await Suite.get(id=suite_id))

    # 添加新关联的套件
    for suite_id in to_add:
        await task.suite.add(await Suite.get(id=suite_id))

    # 保存任务更改
    await task.save()
    return task


# 修改测试任务
# @router.patch('/tasks/{task_id}', summary='修改测试任务')
# async def update_task(task_id: int, item: UpdateTaskForm):
#     task = await TestTask.get_or_none(id=task_id).prefetch_related('suite')
#     if not task:
#         raise HTTPException(status_code=422, detail="任务不存在")
#
#     # 更新任务的基本信息
#     task.name = item.name
#     task.project_id = item.project
#
#     # 获取当前关联的套件ID集合
#     current_suite_ids = {suite.id for suite in task.suite}
#     new_suite_ids = set(item.suite)
#
#     # 计算需要删除和添加的套件ID
#     to_remove = current_suite_ids - new_suite_ids
#     to_add = new_suite_ids - current_suite_ids
#
#     # 删除不再关联的套件
#     for suite_id in to_remove:
#         await task.suite.remove(await Suite.get(id=suite_id))
#
#     # 添加新关联的套件
#     for suite_id in to_add:
#         await task.suite.add(await Suite.get(id=suite_id))
#
#     # 保存任务更改
#     await task.save()
#     # 重新查询以获取最新的任务数据
#     updated_task = await TestTask.get(id=task_id).prefetch_related('suite')
#
#     return {"id": updated_task.pk, "name": updated_task.name, "flow": [flow for flow in updated_task.suite]}
#

# 删除测试任务
@router.delete('/tasks/{task_id}', summary='删除测试任务', status_code=204)
async def del_task(task_id: int):
    task = await TestTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=422, detail="任务不存在")
    await task.delete()
    return {"msg": "删除成功"}


# 运行测试任务
@router.post('/tasks/run', summary='运行测试任务')
async def run_task(item: RunTaskForm):
    print(item)
    async with in_transaction():
        try:
            task = await TestTask.get_or_none(id=item.task).prefetch_related('suite')
            record = await TestRecord.create(task_id=item.task, env_id=item.env, tester=item.tester)
            all_ = 0
            success = 0
            fail = 0
            error = 0
            start_time = time.time()
            result = []
            for suite in task.suite:
                res = await run_scenes(SuiteRunForm(env=item.env, flow=suite.id))
                result.append(res)
                all_ += res['all']
                success += res['success']
                fail += res['fail']
                error += res['error']

            pass_rate = str(round((success / all_) * 100, 2))
            if success == all_:
                status = '成功'
            elif error != 0:
                status = '错误'
            else:
                status = '失败'
            run_time = str(round(time.time() - start_time, 2)) + 's'
            record.all = all_
            record.success = success
            record.fail = fail
            record.error = error
            record.pass_rate = pass_rate
            record.run_time = run_time
            record.status = status
            await record.save()
            info = {
                "all": all_,
                "fail": fail,
                "error": error,
                "success": success,
                "results": result,
            }
            await TestReport.create(record=record, info=info)
        except Exception as e:
            result = ['error']
            raise HTTPException(status_code=422, detail="error")
        return result


# 获取运行记录，传task就是任务的所有记录，传project，就是项目数据看板
@router.get('/records', summary='获取单个任务所有运行记录')
async def get_records(task: Optional[int] = None, project: Optional[int] = None):
    if task:
        records = await TestRecord.filter(task_id=task).select_related('task', 'env').order_by('-create_time')
    elif project:
        records = await TestRecord.filter(task__project=project).select_related('task', 'env').order_by('-create_time')
    else:
        raise HTTPException(status_code=422, detail="参数错误,task和project不能都为空")
    return [{"id": record.pk, "task": record.task.name, "env": record.env.name, "tester": record.tester,
             "all": record.all, "success": record.success, "fail": record.fail, "error": record.error,
             "pass_rate": record.pass_rate, "run_time": record.run_time, "status": record.status,
             "create_time": record.create_time.strftime("%Y-%m-%d %H:%M:%S")
             } for record in records]


# 获取单个测试记录详情
@router.get('/records/{record_id}', summary='获取单个测试记录详情')
async def get_recordInfo(record_id: int):
    record = await TestRecord.get_or_none(id=record_id).prefetch_related('task', 'env')
    if not record:
        raise HTTPException(status_code=422, detail="记录不存在")
    return {
        "id": record.pk,
        "task": record.task.name,
        "env": record.env.name,
        "tester": record.tester,
        "all": record.all,
        "success": record.success,
        "fail": record.fail,
        "error": record.error,
        "pass_rate": record.pass_rate,
        "run_time": record.run_time,
        "status": record.status,
        "create_time": record.create_time
    }


# 获取测试报告
@router.get('/report/{record_id}', summary='获取测试报告')
async def get_report(record_id: int):
    report = await TestReport.get_or_none(record_id=record_id)
    return report
