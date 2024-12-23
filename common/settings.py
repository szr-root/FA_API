# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/06
# @File : settings.py
import os
from pathlib import Path

# ############## 文件存储配置信息 ###############
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_URL = 'files/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'files')


# ############## 数据库的配置信息 ###############
DATABASE = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'songzhaoruizx',
    'database': 'api_fastapi',
}

# ############## 项目中的所有应用的models ###############
INSTALLED_APPS = [
    'apps.users.models',
    'apps.projects.models',
    'apps.Interface.models',
    'apps.Suite.models',
    'apps.TestTask.models',
    'apps.Crontab.models'
]

# ############## tortoise的基本配置 ###############
TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.mysql',
            'credentials': DATABASE
        },
    },
    'apps': {
        'models': {
            'models': ['aerich.models', *INSTALLED_APPS],
            'default_connection': 'default',
        },
    }
}


# ==========================token配置 ==========================
# 64位秘钥
SECRET_KEY = "49bbf2c7a0df9c9a76e9347fe208f8949371d202c386e05ec4ec6a6caf98e452"
# 加密算法
ALGORITHM = "HS256"

# token过期时间
TOKEN_TIMEOUT = 60 * 60 * 24 * 7

# ==========================RabbitMQ配置 ==========================
MQ_CONFIG = {
    'host': '113.45.179.110',
    'port': 5672,
    'queue': 'web_test_queue',
}

# ==========================Redis配置 ==========================
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 1,
    "password": "qwe123"
}
