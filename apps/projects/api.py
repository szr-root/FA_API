# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/06
# @File : api.py
from typing import List

from fastapi import APIRouter, HTTPException
from .models import Project, Env, TestFile
from .schemas import AddProjectForm, ProjectInfo, EditProjectForm, AddEnvForm, EnvInfo, UpdateEnvForm
from ..users.models import Users

router = APIRouter(prefix='/api/testPro', tags=['项目'])


# ############################################# 项目相关 #############################################
# 创建项目
@router.post("/projects", tags=["项目"], summary="创建项目")
async def add_project(item: AddProjectForm):
    leader = await Users.get_or_none(id=item.leader)
    if not leader:
        raise HTTPException(status_code=422, detail="用户不存在")
    project = await Project.create(name=item.name, leader=leader)
    return project


# 获取项目列表
@router.get("/projects", tags=["项目"], summary="获取项目列表", response_model=List[ProjectInfo])
async def get_projects():
    projects = await Project.all().prefetch_related('leader')
    projects = [
        {
            'id': item.id,
            'name': item.name,
            'leader': item.leader.nickname,
            'create_time': item.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        for item in projects]
    return projects


# 获取项目详情
@router.get("/projects/{pro_id}", tags=["项目"], summary="获取项目详情")
async def get_projectInfo(pro_id: int):
    item = await Project.get_or_none(id=pro_id).prefetch_related('leader')
    if not item:
        raise HTTPException(status_code=422, detail="项目不存在")
    project = {
        'name': item.name,
        'leader': item.leader.nickname,
        'create_time': item.create_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return project


# 修改项目
@router.patch("/editProject/{pro_id}", tags=["项目"], summary="修改项目")
async def edit_project(pro_id: int, item: EditProjectForm):
    project = await Project.get_or_none(id=pro_id).prefetch_related('leader')
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")
    if item.leader:
        leader = await Users.get_or_none(id=item.leader)
        item.leader = leader
    await project.update_from_dict(item.dict()).save()
    return {
        "id": project.id,
        "name": project.name,
        'leader': project.leader.nickname,
        'create_time': project.create_time.strftime('%Y-%m-%d %H:%M:%S')
    }


# 删除项目
@router.delete("/Projects/{pro_id}", tags=["项目"], summary="删除项目", status_code=204)
async def del_project(pro_id: int):
    project = await Project.get_or_none(id=pro_id)
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")
    await project.delete()


# ############################################# 环境相关 #############################################
# 创建测试环境
@router.post("/envs", tags=["项目"], summary="创建测试环境")
async def add_env(item: AddEnvForm):
    project = await Project.get_or_none(id=item.project)
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")
    item.project = project
    env = await Env.create(**item.dict())
    return env


# 获取测试环境列表
@router.get("/envs", tags=["项目"], summary="获取测试环境", response_model=list[EnvInfo])
async def get_envs(pro_id: int):
    envs = await Env.all().filter(project=pro_id).prefetch_related('project')
    return [{
        "id": env.id,
        "name": env.name,
        "project": env.project.name
    }
        for env in envs]


# 获取测试环境详情
@router.get("/envInfo", tags=["项目"], summary="获取测试环境详情")
async def get_envInfo(env_id: int):
    env = await Env.get_or_none(id=env_id).prefetch_related('project')
    if not env:
        raise HTTPException(status_code=422, detail="环境不存在")
    return {
        "id": env.id,
        "name": env.name,
        "project": env.project.name,
        "host": env.host,
        "headers": env.headers,
        "db": env.db,
        "global_variable": env.global_variable,
        "debug_global_variable": env.debug_global_variable,
        "global_func": env.global_func
    }


# 修改测试环境
@router.patch("/envs/{env_id}", tags=["项目"], summary="修改测试环境")
async def edit_env(env_id: int, item: UpdateEnvForm):
    env = await Env.get_or_none(id=env_id)
    if not env:
        raise HTTPException(status_code=422, detail="环境不存在")
    await env.update_from_dict(item.dict(exclude_unset=True)).save()
    return env


# 删除测试环境
@router.delete("/envs/{env_id}", tags=["项目"], summary="删除测试环境", status_code=204)
async def del_env(env_id: int):
    env = await Env.get_or_none(id=env_id)
    if not env:
        raise HTTPException(status_code=422, detail="环境不存在")
    await env.delete()


# ############################################# 文件相关 #############################################
# 获取测试文件 todo
@router.get("/testFile", tags=["项目"], summary="获取测试文件")
async def get_testFile():
    testFile = await TestFile.all()
    return testFile
