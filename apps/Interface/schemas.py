# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/11
# @File : schemas.py
from pydantic import BaseModel, Field


class AddInterFaceForm(BaseModel):
    project: int = Field(description="项目id")
    name: str = Field(description="接口名称")
    method: str = Field(description="请求方法", default='GET')
    url: str = Field(description="接口路径")
    type: str = Field(description="接口类型", default='1')


class UpdateInterFaceForm(AddInterFaceForm):
    project: int = Field(description="项目id", default=1)
    name: str = Field(description="接口名称", default='')
    method: str = Field(description="请求方法", default='GET')
    url: str = Field(description="接口路径", default='')
    type: str = Field(description="接口类型", default='1')


class AddInterFaceCaseForm(BaseModel):
    title: str = Field(description="用例标题")
    interface: int = Field(description="关联接口")
    headers: dict = Field(description="请求头", default={})
    request: dict = Field(description="请求参数", default={})
    file: list = Field(description="文件名", default=[])
    setup_script: str = Field(description="前置脚本", default="")
    teardown_script: str = Field(description="后置脚本", default="")


class UpdateInterFaceCaseForm(AddInterFaceCaseForm):
    title: str = Field(description="用例标题", default='')
    interface: int = Field(description="关联接口", default=1)
    headers: dict = Field(description="请求头", default={})
    request: dict = Field(description="请求参数", default={})
    file: list = Field(description="文件名", default=[])
    setup_script: str = Field(description="前置脚本", default="")
    teardown_script: str = Field(description="后置脚本", default="")

