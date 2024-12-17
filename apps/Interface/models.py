# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/11
# @File : models.py

from tortoise import models, fields


class InterFace(models.Model):
    """接口表"""
    Choices = [('1', '项目接口'), ('2', '外部接口')]
    project = fields.ForeignKeyField('models.Project', related_name='interfaces', description='关联项目')
    name = fields.CharField(max_length=50, description='接口名称')
    method = fields.CharField(max_length=10, description='请求方法')
    url = fields.CharField(max_length=100, description='接口路径')
    type = fields.CharField(max_length=20, description='接口类型', choices=Choices)

    def __str__(self):
        return self.name

    class Meta:
        table = 'InterFaces'
        table_description = '接口表'


class InterFaceCase(models.Model):

    """接口用例表"""
    title = fields.CharField(max_length=50, description='用例标题')
    interface = fields.ForeignKeyField('models.InterFace', related_name='cases', description='关联接口')
    headers = fields.JSONField(description='请求头', default=dict, blank=True, null=True)
    request = fields.JSONField(description='请求参数', default=dict, blank=True, null=True)
    file = fields.JSONField(max_length=100, description='文件名', default=list, blank=True, null=True)
    setup_script = fields.TextField(description='前置脚本', default="", blank=True, null=True)
    teardown_script = fields.TextField(description='后置脚本', default="", blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        table = 'InterFaceCases'
        table_description = '接口用例表'
