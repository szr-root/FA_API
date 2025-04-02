# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/06
# @File : api.py
# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/08
# @File : api.py
from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm

from .schemas import RegisterForm, LoginForm, UserInfoSchema, LoginSchema, TokenForm, Token
from .models import Users
from fastapi import APIRouter, HTTPException, Depends
from common import auth

router = APIRouter(prefix='/api/users')


@router.post("/token", tags=["API调试"], summary="api获取token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """仅接口文档调试时生成token使用"""
    user = await Users.get_or_none(username=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    if not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="密码错误")
    uinfo = UserInfoSchema(**user.__dict__)
    token = auth.create_token(uinfo.dict())

    return Token(access_token=token, token_type="bearer")


@router.post("/register/", tags=["用户管理"], summary="用户注册", response_model=UserInfoSchema)
async def register(item: RegisterForm):
    # 校验两次密码是否一致
    if item.password != item.password_confirm:
        raise HTTPException(status_code=422, detail="两次密码不一致")
    # 校验用户名是否已存在
    if await Users.get_or_none(username=item.username):
        raise HTTPException(status_code=422, detail="用户名已存在")
    # 校验邮箱是否已存在
    if item.email and await Users.get_or_none(email=item.email):
        raise HTTPException(status_code=422, detail="邮箱已存在")
    # 校验手机号是否已存在
    if item.mobile and await Users.get_or_none(mobile=item.mobile):
        raise HTTPException(status_code=422, detail="手机号已存在")
    # 注册用户
    item.__dict__.pop('password_confirm')
    # 密码加密
    item.password = auth.get_password_hash(item.password)

    user = await Users.create(**item.dict())
    return UserInfoSchema(**user.__dict__)


@router.post("/login/", tags=["用户管理"], summary="用户登录", response_model=LoginSchema)
async def login(item: LoginForm):
    """登录的逻辑,实现用户名、手机号、邮箱均可以作为账号登录"""
    user1 = await Users.get_or_none(username=item.username)
    user2 = await Users.get_or_none(mobile=item.username)
    user3 = await Users.get_or_none(email=item.username)
    user = user1 or user2 or user3
    if not user:
        raise HTTPException(status_code=422, detail="用户名或密码错误")
    if not auth.verify_password(item.password, user.password):
        raise HTTPException(status_code=422, detail="用户名或密码错误")
    uinfo = UserInfoSchema(**user.__dict__)
    # 账户名密码正确，生成token
    token = auth.create_token(uinfo.dict())
    # 返回token 和用户信息
    return LoginSchema(token=token, user=uinfo)


# 返回用户列表
@router.get("/list/", tags=["用户管理"], summary="用户列表", response_model=list[UserInfoSchema])
async def get_user_list():
    """
    获取用户列表
    :return:
    """
    users = await Users.all()
    return [UserInfoSchema(**user.__dict__) for user in users]


# 校验token
@router.post("/verify/", tags=["用户管理"], summary="校验token", response_model=UserInfoSchema)
async def verify_token(item: TokenForm):
    """
    校验token
    :param item:{"token":xxx}
    :return:
    """
    try:
        userinfo = auth.verify_token(item.token)
    except Exception as e:
        raise HTTPException(422, '校验失败')
    return userinfo


# 刷新token
@router.post("/refresh/", tags=["用户管理"], summary="刷新token", response_model=TokenForm)
async def refresh_token(item: TokenForm):
    """
    刷新token
    :param item:{"token":xxx}
    :return:
    """
    # 校验token，获取token中用户信息
    userinfo = auth.verify_token(item.token)

    # 生成新的token
    return {"token": auth.create_token(userinfo)}
