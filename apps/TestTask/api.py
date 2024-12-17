# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : api.py

from fastapi import APIRouter, HTTPException
from .models import TestTask, TestReport, TestRecord
from .schemas import AddTaskForm, UpdateForm
from ..Suite.models import Suite
from ..projects.models import Project

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


# 修改测试任务 todo
@router.patch('/tasks/{task_id}', summary='修改测试任务')
async def update_task(task_id: int, item: UpdateForm):
    task = await TestTask.get_or_none(id=task_id).select_related('suite')
    if not task:
        raise HTTPException(status_code=422, detail="任务不存在")
    await task.update_from_dict(*item.dict(exclude_unset=True)).save()
    return {"id": task.pk, "name": task.name, "scene": [scene.id for scene in task.suite]}
