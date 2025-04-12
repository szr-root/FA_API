# coding=utf-8
"""
    @project: FA_API
    @file： tencent_cos.py
    @Author：John
    @date：2025/4/12 16:25
"""

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import re
import os
import logging

os.environ['COS_SECRET_ID'] = ''
os.environ['COS_SECRET_KEY'] = ''
Bucket = 'testapi-1301806088'


class URLLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.url = None

    def emit(self, record):
        log_message = record.getMessage()
        match = re.search(r'url=:(https?://[^,]+)', log_message)
        if match:
            self.url = match.group(1)


# 创建日志处理器实例
url_handler = URLLogHandler()

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
# logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.basicConfig(level=logging.INFO, handlers=[url_handler])

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = os.environ['COS_SECRET_ID']
# 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140

secret_key = os.environ['COS_SECRET_KEY']
# 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
region = 'ap-chengdu'  # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
# COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
token = None  # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
scheme = 'https'  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)


# print(sys.stdout)


def upload_file_cos(file_name, file_bytes: bytes):
    """
    上传文件
    :param file_name: 文件路径
    :param file_bytes: 二进制图片数据
    :return:
    """
    response = client.put_object(
        Bucket=Bucket,
        Body=file_bytes,
        Key=file_name,
        EnableMD5=False
    )
    img_url = url_handler.url
    return img_url


def check_file_exists(file_name):
    """
    检查文件是否存在
    :param file_name: 文件路径
    :return:
    """
    response = client.object_exists(
        Bucket=Bucket,
        Key=file_name)
    return response


def del_file(file_name):
    response = client.delete_object(
        Bucket=Bucket,
        Key=file_name
    )


if __name__ == '__main__':
    with open('earth.png', 'rb') as f:
        file_bytes = f.read()
    url = upload_file_cos('earth.png', file_bytes)
    res = check_file_exists('earth.png')
    print(res)
    del_file('earth.png')
    res = check_file_exists('earth.png')
    print('2////',res)
