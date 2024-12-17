# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : models.py
import tortoise.fields
from tortoise import models, fields


class TestTask(models.Model):
    """测试任务表"""
    project = fields.ForeignKeyField('models.Project', related_name='tasks', description='关联项目')
    name = fields.CharField(max_length=50, description='任务名称')
    suite = fields.ManyToManyField('models.Suite', related_name='tasks', description='关联套件')

    def __str__(self):
        return self.name

    class Meta:
        table = 'TestTask'
        table_description = '测试任务'


class TestRecord(models.Model):
    """测试运行记录表"""
    task = fields.ForeignKeyField('models.TestTask', related_name='records', description='关联任务',
                                  on_delete=tortoise.fields.CASCADE)
    env = fields.ForeignKeyField('models.Env', related_name='records', description='关联环境',
                                 on_delete=tortoise.fields.RESTRICT)
    start_time = fields.DatetimeField(auto_now_add=True, description='开始时间')
    all = fields.IntField(description='用例总数', default=0, blank=True)
    success = fields.IntField(description='成功用例数', default=0, blank=True)
    fail = fields.IntField(description='失败用例数', default=0, blank=True)
    error = fields.IntField(description='错误用例数', default=0, blank=True)
    pass_rate = fields.CharField(max_length=10, description='通过率', default='0')
    tester = fields.CharField(max_length=30, description='测试人员')
    end_time = fields.DatetimeField(description='结束时间')
    status = fields.CharField(max_length=10, description='运行状态')

    def __str__(self):
        return str(self.pk)

    class Meta:
        table = 'TestRecord'
        table_description = '测试运行记录'


class TestReport(models.Model):
    """测试报告表"""
    record = fields.ForeignKeyField('models.TestRecord', related_name='report', description='关联记录',
                                    on_delete=tortoise.fields.CASCADE)
    info = fields.JSONField(description='报告信息', default=dict, blank=True)
