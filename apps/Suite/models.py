# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/13
# @File : models.py

from tortoise import models, fields


class Suite(models.Model):
    """测试套件"""
    project = fields.ForeignKeyField('models.Project', related_name='suite')
    name = fields.CharField(max_length=50, description='套件名称')

    def __str__(self):
        return self.name

    class Meta:
        table = 'suite'
        table_description = '测试套件'


class SuiteToCase(models.Model):
    """套件和用例关联表"""
    suite = fields.ForeignKeyField('models.Suite', related_name='suite')
    suite_case = fields.ForeignKeyField('models.InterFaceCase', related_name='icase')
    sort = fields.IntField(description='执行顺序', null=True, blank=True)

    def __str__(self):
        return self.suite_case.title

    class Meta:
        table = 'suite_to_case'
        table_description = '套件中用例执行顺序'
