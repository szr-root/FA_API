# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : api.py

from fastapi import APIRouter, HTTPException
from tortoise.query_utils import Prefetch

from BackEngine.core.runner import TestRunner
from .schemas import AddSuiteForm, AddSuiteToCaseForm, SuiteSchema, UpdateOrder, SuiteRunForm, UpdateSuiteForm
from .models import Suite, SuiteToCase
from apps.projects.models import Project, Env
from ..Interface.models import InterFaceCase

router = APIRouter(prefix='/api/testFlow', tags=['测试套件（业务流）'])


# 创建测试套件
@router.post('/scenes', summary='创建测试套件', status_code=201)
async def create_scenes(item: AddSuiteForm):
    project = await Project.get_or_none(id=item.project)
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")
    item.project = project
    suite = await Suite.create(**item.dict())
    return suite


# 获取测试业务流列表
@router.get('/scenes', summary='获取测试业务流列表', response_model=list[SuiteSchema])
async def get_scenes(project: int):
    project = await Project.get_or_none(id=project)
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")
    suites = await Suite.filter(project=project).all()
    return [SuiteSchema(**{
        "id": suite.id,
        "name": suite.name,
        "project": project.id
    }) for suite in suites]


# 删除测试业务流
@router.delete('/scenes/{suite_id}', status_code=204, summary='删除测试业务流')
async def del_scenes(suite_id: int):
    suite = await Suite.get_or_none(id=suite_id)
    if not suite:
        raise HTTPException(status_code=422, detail="业务流不存在")
    await SuiteToCase.filter(suite=suite).delete()
    await suite.delete()


@router.patch('/scenes/{suite_id}', summary='修改测试业务流')
async def update_scenes(suite_id: int, item: UpdateSuiteForm):
    suite = await Suite.get_or_none(id=suite_id)
    if not suite:
        raise HTTPException(status_code=422, detail="业务流不存在")
    suite.name = item.name
    await suite.save()
    return suite


# 修改测试业务流中用例执行顺序
@router.patch('/icases/order/', summary='修改测试业务流中用例执行顺序')
async def update_scenes(item: list[UpdateOrder]):
    # suite = await Suite.get_or_none(id=suite_id)
    # if not suite:
    #     raise HTTPException(status_code=422, detail="业务流不存在")
    suitecases = []
    for _i in item:
        suite_to_case = await SuiteToCase.get_or_none(id=_i.id)
        suite_to_case.sort = _i.sort
        suitecases.append({'id': suite_to_case.id, 'sort': suite_to_case.sort})
        await suite_to_case.save()
    return suitecases


# 获取业务流中所有用例
@router.get('/icases', summary='获取业务流中所有用例')
async def get_icases(scene: int):
    suite = await Suite.get_or_none(id=scene)
    if not suite:
        raise HTTPException(status_code=422, detail="业务流不存在")

    cases = await SuiteToCase.filter(suite=suite).prefetch_related(
        Prefetch('suite_case', queryset=InterFaceCase.all())
    ).order_by('sort')

    # 提取详细信息
    details = [
        {
            "id": case.id,
            "icase": {
                'id': case.suite_case.id,
                'title': case.suite_case.title,
            },
            "sort": case.sort
        }
        for case in cases
    ]
    return details


# 运行测试业务流
@router.post('/scenes/run', summary='运行测试业务流')
async def run_scenes(item: SuiteRunForm):
    env_id = item.env
    suite_id = item.scene
    env = await Env.get_or_none(id=env_id)
    if not env:
        raise HTTPException(status_code=422, detail="环境不存在")
    suite = await Suite.get_or_none(id=suite_id)
    if not suite:
        raise HTTPException(status_code=422, detail="业务流不存在")

    env_config = {
        'ENV': {
            "host": env.host,
            "headers": env.headers,
            **env.global_variable,
            **env.debug_global_variable
        },
        "DB": env.db,
        "global_func": env.global_func,
    }
    cases = await SuiteToCase.filter(suite_id=suite_id).prefetch_related(
        Prefetch('suite_case', queryset=InterFaceCase.all().select_related('interface'))
    ).order_by('sort')

    cases = [{
        "title": case.suite_case.title,
        "interface": {
            "url": case.suite_case.interface.url,
            "method": case.suite_case.interface.method
        },
        "headers": case.suite_case.headers,
        "request": case.suite_case.request,
        "setup_script": case.suite_case.setup_script,
        "teardown_script": case.suite_case.teardown_script,
    } for case in cases]

    # 组装测试数据
    case_datas = [
        {
            "name": suite.name,
            "Cases": cases
        }
    ]
    # return case_datas
    runner = TestRunner(case_datas, env_config).run()
    return runner[0]


# 向测试业务流中添加测试用例
@router.post('/icases', summary='向测试业务流中添加测试用例',status_code=201)
async def add_icase(item: AddSuiteToCaseForm):
    suite = await Suite.get_or_none(id=item.scene)
    if not suite:
        raise HTTPException(status_code=422, detail="业务流不存在")
    suite_case = await InterFaceCase.get_or_none(id=item.icase)
    if not suite_case:
        raise HTTPException(status_code=422, detail="用例不存在")
    return await SuiteToCase.create(suite=suite, suite_case=suite_case, sort=item.sort)


# 删除业务流中的用例
@router.delete('/icases/{case_id}', summary='删除业务流中的用例', status_code=204)
async def del_icase(case_id: int):
    suite_case = await SuiteToCase.get_or_none(id=case_id)
    if not suite_case:
        raise HTTPException(status_code=422, detail="用例不存在")
    await suite_case.delete()
