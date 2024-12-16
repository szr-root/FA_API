# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : schemas.py

from pydantic import BaseModel, Field


class AddTaskForm(BaseModel):
    name: str = Field(description='任务名称')
    project: int = Field(description='关联项目')
    suite: list[int] = Field(description='关联套件')