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
    suite: int = Field(description='关联套件')
    suite_case: int = Field(description='关联用例')
    sort: int = Field(description='执行顺序', default=1)


class SuiteSchema(BaseModel):
    id: int = Field(description='套件id')
    name: str = Field(description='套件名称')
    project: int = Field(description='关联项目')
