# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/06
# @File : models.py

from tortoise import models, fields


class Project(models.Model):
    """项目表"""
    create_time = fields.DatetimeField(verbose_name='创建时间', help_text='创建时间', auto_now_add=True)
    name = fields.CharField(max_length=50, help_text='项目名称', verbose_name='项目名')
    leader = fields.ForeignKeyField('models.Users', related_name='projects', description='负责人')

    def __str__(self):
        return self.name

    class Meta:
        table = 'Project'
        table_description = "测试项目表"


class Env(models.Model):
    """测试环境表"""
    project = fields.ForeignKeyField('models.Project', related_name='envs', description='所属项目')
    global_variable = fields.JSONField(description='全局变量', default=dict, null=True, blank=True)
    debug_global_variable = fields.JSONField(description='debug模式全局变量',
                                             default=dict, null=True, blank=True)
    db = fields.JSONField(description='数据库配置', default=list, null=True, blank=True)
    headers = fields.JSONField(description='请求头', default=dict, null=True, blank=True)
    global_func = fields.TextField(description='用例工具文件', default="", null=True, blank=True)
    name = fields.CharField(max_length=30, description='测试环境名称')
    host = fields.CharField(description='base_url地址', max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        table = 'Env'
        table_description = "测试环境表"


class TestFile(models.Model):
    """文件上传"""
    file = fields.CharField(max_length=100, description='文件名')
    info = fields.JSONField(description='数据', default=list, blank=True)

    def __str__(self):
        return self.info

    class Meta:
        table = 'File'
        table_description = "测试文件表"
