# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : schemas.py

from pydantic import BaseModel, Field


class AddTaskForm(BaseModel):
    name: str = Field(description='任务名称')
    project: int = Field(description='关联项目')
    flow: list[int] = Field(description='关联套件')


class UpdateTaskForm(BaseModel):
    id: int = Field(description='任务id')
    name: str = Field(description='任务名称')
    flow: list[int] = Field(description='关联套件')


class RunTaskForm(BaseModel):
    env: int = Field(description='关联环境')
    task: int = Field(description='关联任务')
    tester: str = Field(description="执行人")


class SendReportForm(BaseModel):
    record_id: str = Field(description="报告id")
