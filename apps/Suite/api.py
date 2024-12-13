# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : api.py

from fastapi import APIRouter, HTTPException
from .schemas import AddSuiteForm, UpdateSuiteForm, AddSuiteToCaseForm
from .models import Suite, SuiteToCase
from apps.projects.models import Project
from ..Interface.models import InterFaceCase

router = APIRouter(prefix='/api/testFlow', tags=['测试套件（业务流）'])


# 创建测试套件
@router.post('/scenes', summary='创建测试套件')
async def create_scenes(item: AddSuiteForm):
    project = await Project.get_or_none(id=item.project)
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")
    item.project = project
    suite = await Suite.create(**item.dict())
    return suite


# 获取测试业务流列表
@router.get('/scenes', summary='获取测试业务流列表')
async def get_scenes(project: int):
    project = await Project.get_or_none(id=project)
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")
    suite = await Suite.filter(project=project).all()
    return suite


# 获取业务流中所有用例
@router.get('/icases/{suite_id}', summary='获取业务流中所有用例')
async def get_icases(suite_id: int):
    suite = await Suite.get_or_none(id=suite_id).prefetch_related('')
    if not suite:
        raise HTTPException(status_code=422, detail="业务流不存在")
    return await SuiteToCase.filter(suite=suite).all()


# 删除测试业务流
@router.delete('/scenes/{suite_id}', status_code=204, summary='删除测试业务流')
async def del_scenes(suite_id: int):
    suite = await Suite.get_or_none(id=suite_id)
    if not suite:
        raise HTTPException(status_code=422, detail="业务流不存在")
    await SuiteToCase.filter(suite=suite).delete()
    await suite.delete()


# 修改测试业务流
@router.patch('/scenes/{suite_id}',summary='修改测试业务流')
async def update_scenes(suite_id: int, item: UpdateSuiteForm):
    suite = await Suite.get_or_none(id=suite_id)
    if not suite:
        raise HTTPException(status_code=422, detail="业务流不存在")
    await SuiteToCase.update_from_dict(**item.dict(exclude_unset=True))
    return suite




# 运行测试业务流 todo


# 向测试业务流中添加测试用例
@router.post('/icases',summary='向测试业务流中添加测试用例')
async def add_icase(item: AddSuiteToCaseForm):
    suite = await Suite.get_or_none(id=item.suite)
    if not suite:
        raise HTTPException(status_code=422, detail="业务流不存在")
    suite_case = await InterFaceCase.get_or_none(id=item.suite_case)
    if not suite_case:
        raise HTTPException(status_code=422, detail="用例不存在")
    return await SuiteToCase.create(suite=suite, suite_case=suite_case, sort=item.sort)

