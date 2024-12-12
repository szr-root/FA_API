# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/11
# @File : auth.py
"""用户认证和权限校验公共模块

import secrets
key = secrets.token_hex(32)
print(key)
# 49bbf2c7a0df9c9a76e9347fe208f8949371d202c386e05ec4ec6a6caf98e452

"""

import time
import jwt
from passlib.context import CryptContext
from common import settings
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")


async def is_authenticated(token: str = Depends(oauth2_scheme)) -> dict:
    """
    根据token获取用户信息,查询用户是否登录
    :param token:
    :return:
    """
    return verify_token(token)


def verify_password(plain_password, hashed_password):
    """
    校验密码
    :param plain_password: 明文密码
    :param hashed_password: 密文密码
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    哈希密码
    :param password: 明文密码
    :return:
    """
    return pwd_context.hash(password)


def create_token(userinfo: dict):
    # 过期时间
    expire = int(time.time()) + settings.TOKEN_TIMEOUT
    userinfo['exp'] = expire
    # 使用pyjwt生成token
    return jwt.encode(userinfo, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token):
    """校验token"""
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        return data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token校验失败")
