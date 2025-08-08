# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : schemas.py

from pydantic import BaseModel, Field


class AddSuiteForm(BaseModel):
    name: str = Field(description='套件名称')
    project: int = Field(description='关联项目')


class UpdateOrder(BaseModel):
    id: int
    sort: int


class AddSuiteToCaseForm(BaseModel):
    flow: int = Field(description='关联套件')
    icase: int = Field(description='关联用例')
    sort: int = Field(description='执行顺序', default=1)


class UpdateSuiteForm(BaseModel):
    id: int = Field(description='套件id')
    project: int = Field(description='关联项目')
    name: str = Field(description='套件名称')


class SuiteSchema(BaseModel):
    id: int = Field(description='套件id')
    name: str = Field(description='套件名称')
    project: int = Field(description='关联项目')


class SuiteRunForm(BaseModel):
    env: int = Field(description='环境id')
    flow: int = Field(description='套件id')
