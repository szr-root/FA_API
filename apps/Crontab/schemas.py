# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/23
# @File : schemas.py

from pydantic import BaseModel, Field


class Cron(BaseModel):
    minute: str = Field(description="分钟", default="*")
    hour: str = Field(description="小时", default="*")
    day: str = Field(description="日", default="*")
    month: str = Field(description="月", default="*")
    day_of_week: str = Field(description="星期几", default="*")


class CornJobFrom(BaseModel):
    name: str = Field(description="任务名称")
    task: int = Field(description="执行的任务")
    env: int = Field(description="执行环境")
    project: int = Field(description="所属项目")
    state: bool = Field(description="是否启用", default=True)
    run_type: str = Field(description="任务类型", default="Interval")
    date: str = Field(description="指定执行的时间", default="2030-11-25 17:07:00")
    interval: int = Field(description="执行间隔时间", default=60)
    crontab: Cron = Field(description="周期性任务规则",
                          default=Cron(minute="30", hour="*", day="*", month="*", day_of_week="*"))


class UpdagteCornJobFrom(BaseModel):
    name: str = Field(description="任务名称")
    run_type: str = Field(description="任务类型", default="Interval")
    date: str = Field(description="指定执行的时间", default="2030-11-25 17:07:00")
    interval: int = Field(description="执行间隔时间", default=60)
    crontab: Cron = Field(description="周期性任务规则",
                          default=Cron(minute="30", hour="*", day="*", month="*", day_of_week="*"))
