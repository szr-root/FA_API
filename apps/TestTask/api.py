# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : api.py
import json
import time
from typing import Optional

import pytz
from fastapi import APIRouter, HTTPException
from tortoise.transactions import in_transaction

from common.sendfeishu import feishu_url, feishu_send_message
from .models import TestTask, TestReport, TestRecord
from .schemas import AddTaskForm, RunTaskForm, UpdateTaskForm, SendReportForm
from .task_manager import run_task_async, get_task_status, get_all_running_tasks
from ..Suite.api import run_scenes
from ..Suite.models import Suite
from ..Suite.schemas import SuiteRunForm
from ..projects.models import Project

router = APIRouter(prefix="/api/TestTask", tags=["测试任务"])

local_timezone = pytz.timezone('Asia/Shanghai')
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
    tasks = await TestTask.filter(project_id=project)
    data = []
    for task in tasks:
        flows = await task.suite.all()
        data.append({"id": task.pk, "name": task.name, "flow": [flow.id for flow in flows]})
    return data


# 获取单个任务详情
@router.get('/tasks/{task_id}', summary='获取单个任务详情')
async def get_task(task_id: int):
    task = await TestTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=422, detail="任务不存在")
    flows = await task.suite.all()
    data = {"id": task.pk, "name": task.name,
            "flow": [{"id": flow.id, "name": flow.name} for flow in flows]}
    return data


# 向测试任务中添加测试套件
@router.patch('/tasks/{task_id}', summary='向测试任务中添加测试套件')
async def add_icase(item: UpdateTaskForm):
    task = await TestTask.get_or_none(id=item.id)
    # 更新任务的基本信息
    task.name = item.name

    # 获取当前关联的套件ID集合
    current_suite_ids = {suite.id for suite in await task.suite.all()}
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


# 运行测试任务（后台异步执行）
@router.post('/tasks/run', summary='运行测试任务（后台异步）')
async def run_task(item: RunTaskForm):
    """
    提交测试任务到后台执行，立即返回任务ID用于状态查询
    解决原同步执行导致的卡死问题
    """
    try:
        # 验证任务存在
        task = await TestTask.get_or_none(id=item.task)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 使用后台任务管理器异步执行任务
        task_uuid = await run_task_async(item.task, item.env, item.tester)
        
        return {
            "result": "success", 
            "task_uuid": task_uuid,
            "message": "任务已提交到后台执行，请使用任务ID查询执行状态",
            "query_url": f"/api/TestTask/tasks/status/{task_uuid}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"提交测试任务失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"提交测试任务失败: {str(e)}")


# 查询任务执行状态
@router.get('/tasks/status/{task_uuid}', summary='查询测试任务执行状态')
async def get_task_status(task_uuid: str):
    """查询后台任务的执行状态和进度"""
    try:
        status_info = get_task_status(task_uuid)
        
        if not status_info:
            raise HTTPException(status_code=404, detail="任务不存在或已过期")
        
        return {
            "result": "success",
            "task_uuid": task_uuid,
            "status": status_info["status"],
            "progress": status_info["progress"],
            "created_at": status_info["created_at"].isoformat() if status_info["created_at"] else None,
            "started_at": status_info["started_at"].isoformat() if status_info["started_at"] else None,
            "completed_at": status_info["completed_at"].isoformat() if status_info["completed_at"] else None,
            "result": status_info["result"],
            "error": status_info["error"],
            "record_id": status_info["record_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"查询任务状态失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"查询任务状态失败: {str(e)}")


# 获取所有运行中的任务
@router.get('/tasks/running', summary='获取所有运行中的任务')
async def get_running_tasks():
    """获取当前所有正在运行的测试任务"""
    try:
        running_tasks = get_all_running_tasks()
        
        return {
            "result": "success",
            "count": len(running_tasks),
            "tasks": [
                {
                    "task_uuid": task_uuid,
                    "task_id": task_info["task_id"],
                    "tester": task_info["tester"],
                    "status": task_info["status"],
                    "progress": task_info["progress"],
                    "created_at": task_info["created_at"].isoformat() if task_info["created_at"] else None,
                    "started_at": task_info["started_at"].isoformat() if task_info["started_at"] else None
                }
                for task_uuid, task_info in running_tasks.items()
            ]
        }
        
    except Exception as e:
        print(f"获取运行中任务失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取运行中任务失败: {str(e)}")



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


# 发送报告到飞书
@router.post('/send_report', summary='发送报告到飞书')
async def send_report(item: SendReportForm):
    # print(item)
    record_id = int(item.record_id)
    result = await TestReport.get_or_none(record_id=record_id)
    record = await TestRecord.get_or_none(id=record_id).prefetch_related('task', 'env')
    info = {
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
    feishu_send_message(result.info, record_id, info, feishu_url)
