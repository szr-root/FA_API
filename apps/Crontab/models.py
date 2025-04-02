# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/23
# @File : models.py

from tortoise import models, fields


class CronJob(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, description='任务名称')
    project = fields.ForeignKeyField('models.Project', related_name='cronjob', description='所属项目')
    env = fields.ForeignKeyField('models.Env', related_name='cronjob', description='所属环境')
    create_time = fields.DatetimeField(verbose_name='创建时间', help_text='创建时间', auto_now_add=True)
    task = fields.ForeignKeyField('models.TestTask', related_name='cronjob', description='关联任务')
    state = fields.BooleanField(default=True, description="是否启用")
    run_type = fields.CharField(max_length=10, choices=['Interval', 'date', 'crontab'], description="任务类型")
    interval = fields.IntField(default=60, description="执行间隔时间")
    date = fields.DatetimeField(default='2030-01-01 00:00:00', description="指定执行的事件")
    crontab = fields.JSONField(default={'minute': '30', 'hour': '*', 'day': '*', 'month': '*', 'day_of_week': '*'},
                               description="周期性任务规则")

    class Meta:
        table = "crontab"
        table_description = "定时任务表"
