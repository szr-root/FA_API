# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/06
# @File : settings.py
import os
import dotenv
from pathlib import Path

dotenv.load_dotenv('.env')

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
SECRET_KEY = os.getenv('SECRET_KEY')
# 加密算法
ALGORITHM = "HS256"

# token过期时间
TOKEN_TIMEOUT = 60 * 60 * 24 * 7

# ==========================RabbitMQ配置 ==========================
MQ_CONFIG = {
    'host': os.getenv('MQ_HOST'),
    'port': os.getenv('MQ_PORT'),
    'queue': 'web_test_queue',
}

# ==========================Redis配置 ==========================
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 14,
    "password": "songzhaoruizx"
}

# ==========================腾讯存储配置 ==========================
TENCENT_CONFIG={
    "secret_id": os.getenv('COS_SECRET_ID'),
    "secret_key": os.getenv('COS_SECRET_KEY'),
    "bucket": os.getenv('COS_BUCKET')
}