# coding=utf-8
"""
    @project: FA_API
    @file： tencent_cos.py
    @Author：John
    @date：2025/4/12 16:25
"""

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_exception import CosServiceError
import logging
from common import settings

# from .settings import TENCENT_CONFIG

# os.environ['COS_SECRET_ID'] = TENCENT_CONFIG.get('secret_id')
# os.environ['COS_SECRET_KEY'] = TENCENT_CONFIG.get('secret_key')
Bucket = settings.TENCENT_CONFIG.get('bucket')


class URLLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.url = None

    def emit(self, record):
        log_message = record.getMessage()
        match = re.search(r'url=:(https?://[^,]+)', log_message)
        if match:
            self.url = match.group(1)


url_handler = URLLogHandler()
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = settings.TENCENT_CONFIG.get('secret_id')
secret_key = settings.TENCENT_CONFIG.get('secret_key')
region = settings.TENCENT_CONFIG.get('region', 'ap-chengdu')
token = None
scheme = 'https'
bucket = settings.TENCENT_CONFIG.get('bucket')
custom_domain = settings.TENCENT_CONFIG.get('custom_domain')

if not secret_id or not secret_key or not bucket:
    raise RuntimeError('COS配置缺失：请在环境变量中设置 COS_SECRET_ID、COS_SECRET_KEY、COS_BUCKET')

if '-' not in bucket:
    logger.warning('COS Bucket 看起来不包含 AppId 后缀，标准格式为 <BucketName-APPID>')

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)


# print(sys.stdout)


def _build_object_url(key: str) -> str:
    if custom_domain:
        return f'https://{custom_domain}/{key}'
    return f'https://{bucket}.cos.{region}.myqcloud.com/{key}'


def upload_file_cos(file_name, file_bytes: bytes, content_type: str | None = None):
    """
    上传文件
    :param file_name: 文件路径
    :param file_bytes: 二进制图片数据
    :return:
    """
    try:
        params = {
            'Bucket': bucket,
            'Body': file_bytes,
            'Key': file_name,
            'EnableMD5': False
        }
        if content_type:
            params['ContentType'] = content_type
        client.put_object(**params)
        return _build_object_url(file_name)
    except CosServiceError as e:
        logger.error(f'COS上传失败: code={e.get_error_code()} msg={e.get_error_msg()} request_id={e.get_request_id()}')
        raise


def check_file_exists(file_name):
    """
    检查文件是否存在
    :param file_name: 文件路径
    :return:
    """
    try:
        return client.object_exists(Bucket=bucket, Key=file_name)
    except CosServiceError as e:
        logger.error(f'COS检查失败: code={e.get_error_code()} msg={e.get_error_msg()} request_id={e.get_request_id()}')
        return False


def del_file(file_name):
    try:
        client.delete_object(Bucket=bucket, Key=file_name)
        return True
    except CosServiceError as e:
        logger.error(f'COS删除失败: code={e.get_error_code()} msg={e.get_error_msg()} request_id={e.get_request_id()}')
        return False


if __name__ == '__main__':
    # with open('file.txt', 'r') as f:
    #     file_bytes = f.read()
    # url = upload_file_cos('file.txt', file_bytes)
    # res = check_file_exists('file.txt')
    # print(res)
    del_file('IPS.txt')
    res = check_file_exists('IPS.txt')
    print('2////', res)
