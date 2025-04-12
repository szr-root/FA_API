# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/06
# @File : api.py
import json
import os
from typing import List
from fastapi.responses import FileResponse
from fastapi import APIRouter, HTTPException, File, UploadFile

from common import settings
from .models import Project, Env, TestFile
from .schemas import AddProjectForm, ProjectInfo, EditProjectForm, AddEnvForm, EnvInfo, UpdateEnvForm
from ..users.models import Users
from common.tencent_cos import upload_file_cos,check_file_exists


router = APIRouter(prefix='/api/testPro', tags=['项目'])
file_router = APIRouter(prefix='', tags=['文件'])


# ############################################# 项目相关 #############################################
# 创建项目
@router.post("/projects", tags=["项目"], summary="创建项目", status_code=201)
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
        leader = await Users.get_or_none(nickname=item.leader)
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
@router.post("/envs", tags=["项目"], summary="创建测试环境", status_code=201)
async def add_env(item: AddEnvForm):
    project = await Project.get_or_none(id=item.project)
    if not project:
        raise HTTPException(status_code=422, detail="项目不存在")
    item.project = project
    env = await Env.create(**item.dict())
    return env


# 获取测试环境列表
@router.get("/envs", tags=["项目"], summary="获取测试环境")
async def get_envs(project: int):
    envs = await Env.all().filter(project=project).prefetch_related('project')
    return [{
        "id": env.id,
        "name": env.name,
        "project": env.project.id,
        "host": env.host,
        "headers": env.headers,
        "db": env.db,
        "global_variable": env.global_variable,
        "debug_global_variable": env.debug_global_variable,
        "global_func": env.global_func
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

# 上传文件
@router.post("/files", tags=["项目"], summary="创建测试文件", status_code=201)
async def add_testfile(file: UploadFile):
    size = file.size
    name = file.filename
    if size > 1024 * 1024 * 5:
        raise HTTPException(detail="文件大小不能超过5M", status_code=400)

    if check_file_exists(name):
        raise HTTPException(detail="文件已存在", status_code=400)

    # file_path = settings.MEDIA_ROOT + '/' + name
    # if os.path.isfile(file_path):
    #     raise HTTPException(detail="文件已存在", status_code=400)

    file_type = file.content_type
    # 修改info字段值
    info = json.dumps([name, file_type])
    # os.makedirs(os.path.dirname(file_path), exist_ok=True)
    upload_file_cos(file_name=name, file_bytes=file.file.read())
    testfile = await TestFile.create(file=name, info=info)
    return testfile


# 获取测试文件
@router.get("/files", tags=["项目"], summary="获取测试文件")
async def get_testfile():
    test_files = await TestFile.all()
    return [testfile for testfile in test_files]


# 删除测试文件
@router.delete("/files/{file_id}", tags=["项目"], summary="删除测试文件", status_code=204)
async def del_testfile(file_id: int):
    testfile = await TestFile.get_or_none(id=file_id)
    if not testfile:
        raise HTTPException(status_code=422, detail="文件不存在")
    file_path = settings.MEDIA_ROOT + '/' + testfile.file
    os.remove(file_path)
    await testfile.delete()


# 展示文件
@file_router.get("/files/{file_name}", tags=["项目"], summary="展示测试文件")
async def show_testfile(file_name: str):
    testfile = await TestFile.get_or_none(file=file_name)
    if not testfile:
        raise HTTPException(status_code=422, detail="文件不存在")
    file_path = settings.MEDIA_ROOT + '/' + testfile.file
    # 检查文件是否存在目录
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="files目录中找不到文件")
    # 创建 FileResponse 对象
    response = FileResponse(file_path, filename=testfile.file)

    # 设置 Content-Type
    content_type = 'image/jpeg'
    if file_path.endswith('.png'):
        content_type = 'image/png'
    elif file_path.endswith('.gif'):
        content_type = 'image/gif'
    elif file_path.endswith('.mp4'):
        content_type = 'video/mp4'
    response.headers['Content-Type'] = content_type
    # 设置 Content-Disposition
    response.headers['Content-Disposition'] = f'inline; filename="{testfile.file}"'
    return response
