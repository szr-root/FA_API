# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/06
# @File : models.py

from tortoise import models, fields


class Users(models.Model):
    """用户模型"""
    id = fields.IntField(pk=True, description="用户id")
    username = fields.CharField(max_length=32, unique=True, description="用户名")
    password = fields.CharField(max_length=128, description="密码")
    nickname = fields.CharField(max_length=32, description="用户昵称")
    email = fields.CharField(max_length=255, description="邮箱", default="", null=True, blank=True)
    mobile = fields.CharField(max_length=128, null=True, blank=True, description="手机号", default="")
    is_active = fields.BooleanField(default=True, description="是否激活")
    is_superuser = fields.BooleanField(default=False, description="是否是超级管理员")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    def __str__(self):
        return self.nickname

    class Meta:
        table = "users"
        table_description = "用户表"
