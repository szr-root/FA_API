# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : api.py

from fastapi import APIRouter, HTTPException
from .models import TestTask, TestReport, TestRecord
from .schemas import AddTaskForm
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
    suite = await Suite.get_or_none(id=item.suite)
    if not suite:
        raise HTTPException(status_code=422, detail="套件不存在")
    item.suite = suite
    task = await TestTask.create(**item.dict())
    return task
