# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/11
# @File : api.py

from fastapi import APIRouter, HTTPException
from .models import InterFace, InterFaceCase
from .schemas import AddInterFaceForm, UpdateInterFaceForm, AddInterFaceCaseForm, UpdateInterFaceCaseForm
from apps.projects.models import Project, Env
from BackEngine.core.runner import TestRunner

router = APIRouter(prefix='/api/TestInterFace', tags=['接口/用例管理'])


# ############################################# 接口相关 #############################################
# 创建接口
@router.post("/interfaces", summary="创建接口")
async def create_interFace(item: AddInterFaceForm):
    """
    创建接口
    """
    project = await Project.get_or_none(id=item.project)
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")
    item.project = project
    interface = await InterFace.create(**item.dict())
    return interface


# 获取接口列表
@router.get("/interfaces", summary="获取接口列表")
async def get_interfaces(pro_id: int):
    """
    获取接口列表
    """
    project = await Project.get_or_none(id=pro_id)
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")

    interfaces = await InterFace.filter(project=project)
    return [{
        "id": interface.id,
        "project": project.name,
        "name": interface.name,
        "method": interface.method,
        "url": interface.url,
        "type": interface.type
    } for interface in interfaces]


# 编辑接口
@router.patch("/interfaces/{_id}", summary="编辑接口")
async def update_interface(_id: int, item: UpdateInterFaceForm):
    """
    编辑接口
    """
    interface = await InterFace.get_or_none(id=_id)
    if not interface:
        raise HTTPException(status_code=422, detail="接口不存在")
    await interface.update_from_dict(item.dict(exclude_unset=True)).save()
    return interface


# 删除接口
@router.delete("/interfaces/{_id}", summary="删除接口", status_code=204)
async def del_interface(_id: int):
    """
    删除接口
    """
    interface = await InterFace.get_or_none(id=_id)
    if not interface:
        raise HTTPException(status_code=422, detail="接口不存在")
    await interface.delete()


# ############################################# 用例相关 #############################################
# 添加测试用例
@router.post("/cases", summary="添加测试用例")
async def add_case(item: AddInterFaceCaseForm):
    interface = await InterFace.get_or_none(id=item.interface)
    if not interface:
        raise HTTPException(status_code=422, detail="接口不存在")
    item.interface = interface
    return await InterFaceCase.create(**item.dict())


# 获取用例详情的接口
@router.get("/cases/{case_id}", summary="获取用例详情")
async def get_case(case_id: int):
    case = await InterFaceCase.get_or_none(id=case_id)
    if not case:
        raise HTTPException(status_code=422, detail="用例不存在")
    return case


# 修改用例
@router.patch("/cases/{case_id}", summary="修改用例")
async def edit_case(case_id: int, item: UpdateInterFaceCaseForm):
    case = await InterFaceCase.get_or_none(id=case_id)
    if not case:
        raise HTTPException(status_code=422, detail="用例不存在")
    await case.update_from_dict(item.dict(exclude_unset=True)).save()
    return case


# 删除用例
@router.delete("/cases/{case_id}", summary="删除用例", status_code=204)
async def del_case(case_id: int):
    case = await InterFaceCase.get_or_none(id=case_id)
    if not case:
        raise HTTPException(status_code=422, detail="用例不存在")
    await case.delete()


# 运行用例
@router.post("/cases/run", summary="运行用例")
async def run_case(env_id: int, cases: dict):
    """
    {
        "title": "登录成功用例",
        "interface":
             {
                 "url": "/account/login/",
                 "method": "post"
             },
             "headers":
             {
                 "Content-Type": "application/json"
             },
             "request": {
                 "json": {
                     "username": "teemo",
                     "password": "666666"
                 }
             },
             "setup_script": "",
             "teardown_script": ""
    }
    """
    if not all([env_id, cases]):
        return "参数错误，env和cases不能为空"
    env = await Env.get_or_none(id=env_id)
    if not env:
        return "环境不存在"
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

    # 组装测试数据
    case_datas = [
        {
            "name": "调试运行",
            "Cases": [cases]
        }
    ]
    runner = TestRunner(case_datas, env_config).run()
    # 调用引擎的run_test方法
    # result, ENV = run_test(case_data=cases_datas, env_config=env_config, debug=True)
    # 将运行的环境变量保存到测试环境debug_global_variable中
    # env.debug_global_variable = ENV
    # env.save()
    return runner
    # return Response(result['results'][0]['cases'][0])
