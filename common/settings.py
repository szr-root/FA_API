# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/12/06
# @File : settings.py
import os
from dotenv import load_dotenv
from pathlib import Path


env_path = Path(__file__).resolve().parent / '.env'
print(env_path)
if env_path.exists():
    print(f"加载 .env 文件: {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"⚠️ .env 文件未找到: {env_path}")


# ############## 文件存储配置信息 ###############
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_URL = 'files/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'files')


# ############## 数据库的配置信息 ###############
DATABASE = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database':os.getenv('DB_NAME'),
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
    'queue': 'queue',
    'username': os.getenv('MQ_USERNAME', 'guest'),  # 默认用户名
    'password': os.getenv('MQ_PASSWORD', 'guest'),  # 默认密码
    'virtual_host': os.getenv('MQ_VHOST', '/'),     # 虚拟主机，默认为/
}

# ==========================Redis配置 ==========================
REDIS_CONFIG = {
    "host": os.getenv('REDIS_HOST', '192.168.50.129'),
    "port": int(os.getenv('REDIS_PORT', 6379)),
    "db": int(os.getenv('REDIS_DB', 14)),
    "password": os.getenv('REDIS_PASSWORD', 'ufo123')
}


# ==========================腾讯存储配置 ==========================
TENCENT_CONFIG={
    "secret_id": os.getenv('COS_SECRET_ID'),
    "secret_key": os.getenv('COS_SECRET_KEY'),
    "bucket": os.getenv('COS_BUCKET'),
    "region": os.getenv('COS_REGION', 'ap-chengdu'),
    "custom_domain": os.getenv('COS_CUSTOM_DOMAIN', None)
}

if __name__ == '__main__':
    print(TENCENT_CONFIG)
