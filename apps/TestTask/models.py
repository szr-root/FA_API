# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : models.py

from tortoise import models, fields


class TestTask(models.Model):
    name = fields.CharField(max_length=50, description='任务名称')
    project = fields.ForeignKeyField('models.Project', related_name='pro_task')
    suite = fields.ManyToManyField('models.Suite', related_name='task')

    def __str__(self):
        return self.name

    class Meta:
        table = 'TestTask'
        table_description = '测试任务'


class TestRecord(models.Model):
    task = fields.ForeignKeyField('models.TestTask', related_name='record')
    env = fields.ForeignKeyField('models.Env', related_name='record')
    all = fields.IntField(description='总用例数')
    fail = fields.IntField(description='失败用例数')
    success = fields.IntField(description='成功用例数')
    error = fields.IntField(description='错误用例数')
    pass_rate = fields.FloatField(description='通过率')
    tester = fields.CharField(max_length=50, description='执行人')
    status = fields.CharField(max_length=20, description='执行状态')
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间')

    def __str__(self):
        return str(self.pk)

    class Meta:
        table = 'testRecord'
        table_description = '运行记录表'


class TestReport(models.Model):
    record = fields.ForeignKeyField('models.TestRecord', related_name='report')
    info = fields.JSONField(description='报告信息', default=dict, blank=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        table = 'testReport'
        table_description = '报告表'
