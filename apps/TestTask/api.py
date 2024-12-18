# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : api.py

from fastapi import APIRouter, HTTPException
from tortoise.query_utils import Prefetch

from .models import TestTask, TestReport, TestRecord
from .schemas import AddTaskForm, UpdateForm, RunTaskForm
from ..Interface.models import InterFaceCase
from ..Suite.api import run_scenes
from ..Suite.models import Suite, SuiteToCase
from ..Suite.schemas import SuiteRunForm
from ..projects.models import Project, Env

router = APIRouter(prefix="/api/testTask", tags=["测试任务"])


# 创建测试任务
@router.post('/tasks', summary='创建测试任务')
async def create_task(item: AddTaskForm):
    project = await Project.get_or_none(id=item.project)
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")
    item.project = project
    # 获取所有套件
    suites = await Suite.filter(id__in=item.suite)
    if len(suites) != len(item.suite):
        raise HTTPException(status_code=422, detail="部分套件不存在")
        # 创建测试任务，排除多对多字段
    task_data = item.dict(exclude={'suite'})
    task = await TestTask.create(**task_data)
    # 关联套件
    await task.suite.add(*suites)

    return {"id": task.pk, "name": task.name, "scene": [scene.id for scene in suites]}


# 查询所有测试任务
@router.get('/tasks', summary='查询所有测试任务')
async def get_tasks(project: int):
    tasks = await TestTask.filter(project=project).prefetch_related('suite')
    return [{"id": task.pk, "name": task.name, "scene": [scene.id for scene in task.suite]} for task in tasks]


# 获取单个任务详情
@router.get('/tasks/{task_id}', summary='获取单个任务详情')
async def get_task(task_id: int):
    task = await TestTask.get_or_none(id=task_id).prefetch_related('suite')
    if not task:
        raise HTTPException(status_code=422, detail="任务不存在")
    data = {"id": task.pk, "name": task.name,
            "scene": [{
                "id": scene.id, "name": scene.name
            } for scene in task.suite]}
    return data


# 修改测试任务
@router.patch('/tasks/{task_id}', summary='修改测试任务')
async def update_task(task_id: int, item: UpdateForm):
    task = await TestTask.get_or_none(id=task_id).prefetch_related('suite')
    if not task:
        raise HTTPException(status_code=422, detail="任务不存在")

    # 更新任务的基本信息
    task.name = item.name
    task.project_id = item.project

    # 获取当前关联的套件ID集合
    current_suite_ids = {suite.id for suite in task.suite}
    new_suite_ids = set(item.suite)

    # 计算需要删除和添加的套件ID
    to_remove = current_suite_ids - new_suite_ids
    to_add = new_suite_ids - current_suite_ids

    # 删除不再关联的套件
    for suite_id in to_remove:
        await task.suite.remove(await Suite.get(id=suite_id))

    # 添加新关联的套件
    for suite_id in to_add:
        await task.suite.add(await Suite.get(id=suite_id))

    # 保存任务更改
    await task.save()
    # 重新查询以获取最新的任务数据
    updated_task = await TestTask.get(id=task_id).prefetch_related('suite')

    return {"id": updated_task.pk, "name": updated_task.name, "scene": [scene for scene in updated_task.suite]}


# 删除测试任务
@router.delete('/tasks/{task_id}', summary='删除测试任务')
async def del_task(task_id: int):
    task = await TestTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=422, detail="任务不存在")
    await task.delete()
    return {"msg": "删除成功"}


# 运行测试任务
@router.post('/tasks/run', summary='运行测试任务')
async def run_task(item: RunTaskForm):
    task = await TestTask.get_or_none(id=item.task).prefetch_related('suite')
    result = []
    for suite in task.suite:
        res = await run_scenes(SuiteRunForm(**{"env": item.env, "suite": suite.id}))
        result.append(res)

    return result
