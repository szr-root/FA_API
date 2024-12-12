# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/06
# @File : schemas.py

from pydantic import BaseModel, Field


# from datetime import datetime


class AddProjectForm(BaseModel):
    name: str = Field(description="项目名称")
    leader: int = Field(description="创建者")


class ProjectInfo(BaseModel):
    id: int = Field(description="项目id")
    name: str = Field(description="项目名称")
    leader: str = Field(description="创建者")
    create_time: str = Field(description="创建时间")


class EditProjectForm(AddProjectForm):
    name: str = Field(description="项目名称", default='')
    leader: int = Field(description="创建者", default='')


class AddEnvForm(BaseModel):
    name: str = Field(description="环境名称")
    db: list = Field(description="数据库配置", default=[])
    debug_global_variable: dict = Field(description="debug模式全局变量", default={})
    global_func: str = Field(description="用例工具文件", default="")
    global_variable: dict = Field(description="全局变量", default={})
    headers: dict = Field(description="请求头", default={})
    host: str = Field(description="base_url地址", default="")
    project: int = Field(description="所属项目")


class EnvInfo(BaseModel):
    id: int = Field(description="环境id")
    name: str = Field(description="环境名称")
    project: str = Field(description="所属项目")


class UpdateEnvForm(AddEnvForm):
    name: str = Field(description="环境名称", default='')
    db: list = Field(description="数据库配置", default=[])
    debug_global_variable: dict = Field(description="debug模式全局变量", default={})
    global_func: str = Field(description="用例工具文件", default="")
    global_variable: dict = Field(description="全局变量", default={})
    headers: dict = Field(description="请求头", default={})
    host: str = Field(description="base_url地址", default="")
    project: int = Field(description="所属项目", default=0)
