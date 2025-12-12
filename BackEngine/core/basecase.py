# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/06/19
# @File : basecase.py

import re
import time
import asyncio
import requests
# 导入内置的测试工具函数
from requests.structures import CaseInsensitiveDict

from BackEngine.core import testtools as my_functools
from jsonpath import jsonpath
from BackEngine.core.caselog import CaseLogHandel

from BackEngine.core.dbclient import DBClient

import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# 定义一个全局变量用来保存测试执行环境的数据
# ENV = {}
# 创建一个数据库连接对象
db = DBClient()


# items = [{
#     "name": "local",
#     "type": "mysql",
#     "config": {"host": "127.0.0.1",
#                "port": 3306,
#                "user": "root",
#                "password": "songzhaoruizx"
#                }
# }]
# db.init_connect(items)


# 创建一个数据库连接对象
# db = DBClient()


class BaseCase(CaseLogHandel):
    """用例执行的基本父类"""

    def __run_script(self, data, env_object):
        """专门执行前后置脚本的函数"""
        # 在前后置脚本的执行环境中内置一些变量
        test = self
        # global_val = env
        # global ENV
        # ENV = env

        print = self.print_log
        # 获取用例的前置脚本
        setup_script = data.get('setup_script')
        # 使用执行器函数执行python的脚步代码
        self.info_log("*****执行前置脚本*****")
        exec(setup_script)
        # 接受传进来的响应结果
        response = yield
        self.info_log("*****执行后置脚本*****")
        teardown_script = data.get('teardown_script')
        exec(teardown_script)
        yield

    def __setup_script(self, data, env, env_object):
        """
        脚本执行前
        :param data:
        :return:
        """
        # 使用脚本执行器函数创建一个生成器对象
        self.env_object = env_object
        self.script_hook = self.__run_script(data, env_object)
        # 执行前置脚步（执行生成器中的代码）
        next(self.script_hook)

    def __teardown_script(self, response):
        """
        脚本执行后
        :param data:
        :return:
        """
        # 执行后置脚本
        # next(self.script_hook)
        self.script_hook.send(response)
        # 删除生成器对象
        delattr(self, 'script_hook')

    def __handler_requests_data(self, data, env):
        """处理请求数据的方法"""
        # global ENV
        request_data = {}
        # 1、处理请求的url
        request_data["method"] = data['interface']['method']
        url = data['interface']['url']
        if not url.startswith('http'):
            # 和base_url进行拼接
            url = env.get('ENV').get('host') + url
        request_data["url"] = url
        self.url = url
        self.method = data['interface']['method']
        # 2、处理请求的headers
        # 获取全局请求头
        headers: dict = env.get('ENV').get('headers')
        # 将全局请求头和当前用例中的请求头进行合并
        headers.update(data['headers'])
        request_data['headers'] = headers
        self.request_headers = headers
        # 3、处理请求的请求参数
        request = data['request']
        # 查询参数
        request_data['params'] = request.get('params')
        # json参数：contentType:application/json
        # 表单参数：contentType:application/x-www-form-urlencoded
        # 文件上传：contentType:multipart/form-data;
        # 请求体参数（json,表单，文件上传）
        if headers.get('Content-Type') is not None:
            if headers.get('Content-Type') == 'application/json':
                request_data['json'] = request.get('json')
                self.request_body = request.get('json')
            if headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                request_data['data'] = request.get('data')
                self.request_body = request.get('data')
            elif 'multipart/form-data' in headers.get('Content-Type'):
                request_data['files'] = request.get('files')
                self.request_body = request.get('files')
        else:
            request_data['json'] = request.get('json')
            self.request_body = request.get('json')
        # 替换用例中的变量
        request_data = self.replace_data(request_data, env)
        self.info_log("===发送【 ", request_data["method"].upper(), " 】请求，请求地址是:", request_data["url"])
        return request_data

    def replace_data(self, data, env):
        """替换用例中的变量"""
        # 数据替换的规则
        pattern = r'\${{(.+?)}}'
        # 将传入的参数转换为字符串
        data = str(data)
        while re.search(pattern, data):
            # 获取匹配到的内容
            match = re.search(pattern, data)
            # 获取匹配到的内容中的变量
            key = match.group(1)
            # 获取全局变量中的值
            value = env.get('ENV').get(key)
            self.info_log("开始替换变量, 将 ", key, " 替换成 ", value)
            # 将匹配到的内容中的变量替换为全局变量中的值
            data = data.replace(match.group(), str(value))

        return eval(data)

    def convert_to_dict(self, obj):
        """Recursively converts a CaseInsensitiveDict to a regular dict."""
        if isinstance(obj, CaseInsensitiveDict):
            return dict(obj)
        elif isinstance(obj, dict):
            return {k: self.convert_to_dict(v) for k, v in obj.items()}
        elif hasattr(obj, '__dict__'):
            return self.convert_to_dict(vars(obj))
        elif isinstance(obj, list):
            return [self.convert_to_dict(element) for element in obj]
        else:
            return obj

    def __send_request(self, data, env):
        """
        发送请求的方法
        :param data:
        :return:
        """
        # 处理用例的请求数据(替换请求参数中的变量，将数据转换为requests发送请求所需要的格式)
        request_data = self.__handler_requests_data(data, env)
        start_time = time.time()
        # 发送请求
        response = requests.request(**request_data)
        self.requests_header = self.convert_to_dict(response.request.headers)
        self.response_header = self.convert_to_dict(response.headers)
        self.response_body = response.text
        # 解密
        # decrypt_py = ENV.get('decrypt_py')
        decrypt_py = env.get('decrypt_py')

        if decrypt_py is not None and response.status_code == 200:
            decrypt_py = decrypt_py.strip()
            if decrypt_py != '[]':
                self.info_log("*****执行解密脚本*****")
                text = response.text
                # 定义一个命名空间字典用于存储 exec 执行后的变量
                namespace = {'text': text}
                exec(decrypt_py, globals(), namespace)
                # 从命名空间中获取 json_data
                json_data_result = namespace.get('json_data', None)
                # 输出结果
                # print(json_data_result)
                self.response_body = json.dumps(json_data_result)
                self.info_log("*****完成解密*****")
                # self.requests_body = response.request.body.decode('utf-8')
        self.run_time = str(round(time.time() - start_time, 2)) + 's'
        self.status_code = response.status_code

        # 返回响应对象
        return self.response_body

    def perform(self, data, env, env_object):
        """
        执行单条用例的入口方法
        :param data:
        :return:
        """
        self.title = data.get('title')
        self.data = data
        self.info_log('===开始执行用例：', self.title, '===')
        # 执行前置脚本
        self.__setup_script(data, env, env_object)
        # 发送请求
        response = self.__send_request(data, env)
        # 执行后置脚本
        self.__teardown_script(response)

    def async_io_operation(self):
        # 同步执行异步保存操作
        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，使用asyncio.create_task()而不是run_until_complete
                # 在运行的事件循环中，我们不能使用run_until_complete
                import threading
                if threading.current_thread() is threading.main_thread():
                    # 在主线程中，可以创建任务但不能等待
                    loop.create_task(self.env_object.save())
                else:
                    # 在非主线程中，需要新的处理方式
                    asyncio.run_coroutine_threadsafe(self.env_object.save(), loop)
            else:
                # 如果没有运行中的事件循环，直接运行
                loop.run_until_complete(self.env_object.save())
        except RuntimeError:
            # 如果没有事件循环，创建新的
            asyncio.run(self.env_object.save())

    def save_env_variable(self, name, value):
        """
        保存环境变量
        :param name:
        :param value:
        :return:
        """
        self.info_log(f"设置局部变量{name}:", value)
        self.env_object.debug_global_variable[name] = value
        self.async_io_operation()

    def save_global_variable(self, name, value):
        """
        保存测试运行环境的变量
        :param data:
        :return:
        """
        self.info_log(f"设置全局变量{name}:", value)
        # self.info_log(f"{ENV['ENV']['host']}")
        self.env_object.global_variable[name] = value
        self.async_io_operation()
        # 同步执行异步保存操作
        #
        # try:
        #     # 尝试获取当前事件循环
        #     loop = asyncio.get_event_loop()
        #     if loop.is_running():
        #         # 如果事件循环正在运行，创建任务
        #         task = loop.create_task(self.env_object.save())
        #         # 等待任务完成
        #         loop.run_until_complete(task)
        #     else:
        #         # 如果没有运行中的事件循环，直接运行
        #         loop.run_until_complete(self.env_object.save())
        # except RuntimeError:
        #     # 如果没有事件循环，创建新的
        #     asyncio.run(self.env_object.save())

    def get_env_variable(self, name):
        return self.env_object.debug_global_variable.get(name)

    def del_env_variable(self, name):
        """
        删除环境变量
        :param name:
        :return:
        """
        self.info_log("删除环境变量:", name)
        del self.env_object.debug_global_variable[name]
        self.async_io_operation()
        pass

    def del_global_variable(self, name):
        """
        删除测试运行环境的变量
        :param name:
        :return:
        """
        self.info_log("删除全局变量:", name)
        del self.env_object.global_variable[name]
        self.async_io_operation()
        pass

    def json_extract(self, obj, ext):
        """
        提取json数据的方法，返回提取到的数据值
        :param obj:
        :param ext:
        :return:
        """
        self.info_log("----通过jsonpath提取数据:", ext)
        res = jsonpath(obj, ext)
        value = res[0] if res else ''
        self.info_log("提取结果：", value)
        return value

    def json_extract_list(self, obj, ext):
        """
        提取json数据的方法,返回包含所有数据的列表
        :param obj:
        :param ext:
        :return:
        """
        self.info_log("----通过jsonpath提取数据:", ext)
        res = jsonpath(obj, ext)
        value = res if res else []
        self.info_log("提取结果：", value)
        return value

    def re_extract(self, obj, ext):
        """
        提取正则表达式数据的方法，返回提取到的数据值
        :param obj: 数据源
        :param ext:正则提取表达式
        :return:
        """
        self.info_log("----通过正则表达式提取数据:", ext)
        if not isinstance(obj, str):
            obj = str(obj)
        self.debug_log("数据源：", obj)
        value = re.search(ext, obj)
        value = value.group(1) if value else ''
        self.debug_log('提取的数据值为：', value)
        return value

    # def assertion(self, method, expected, actual,*args, **kwargs):
    def assertion(self, method, expected, actual):
        """
        :param method: 断言的方法
        :param expected: 预期结果
        :param actual: 实际结果的值
        :return:
        """
        # self.info_log(assert_list)
        methods_map = {
            '相等': lambda x, y: x == y,
            '不相等': lambda x, y: x != y,
            '大于': lambda x, y: x > y,
            '大于等于': lambda x, y: x >= y,
            '小于': lambda x, y: x < y,
            '小于等于': lambda x, y: x <= y,
            '不包含': lambda x, y: x not in y,
            '包含': lambda x, y: x in y,
        }
        self.info_log('----------断言----------')
        self.debug_log('比较方式:{}'.format(method))
        self.debug_log('预期结果:{}'.format(expected))
        self.debug_log('实际结果:{}'.format(actual))
        assert_method = methods_map.get(method)
        if assert_method:
            if assert_method(expected, actual):
                self.info_log("断言通过!")
                # self.info_log(self.)
                self.status = "成功"
            else:
                self.info_log(f"断言 {expected} {method} {actual}失败!")
                self.status = "失败"
                raise AssertionError('断言失败')
        else:
            raise TypeError('断言比较方法{},不支持!'.format(method))


if __name__ == '__main__':
    ENV = {}
    testcase = {
        "title": "登录成功用例",
        "interface":
            {
                "url": "/api/users/login/",
                "method": "post",
            },
        "headers":
            {
                "Content-Type": "application/json",
            },
        "request": {
            "params": {},
            "json": {
                "username": "admin",
                "password": "admin"
            },
        },
        "setup_script": open('../setup_script.txt', 'r', encoding='utf-8').read(),
        "teardown_script": open('../teardown_script.txt', 'r', encoding='utf-8').read(),

    }
    test_env_data = {
        "base_url": "http://172.20.20.54:8001",
        "headers": {
            "Content-Type": "application/json"
        },
        # 用来存放全局变量（用例执行过程中需要存储的变量）
        "Envs": {
            "username": "123qwe",
            "password": "666666"
        },
        "my_functools": open("../my_functools.py", 'r', encoding='utf-8').read(),
        "db": {
            "name": "local",
            "type": "mysql",
            "config": {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "songzhaoruizx"
            }
        }
    }

    # 初始数据库连接
    db.init_connect(test_env_data.pop('db'))

    ENV.update(test_env_data)

    # 通过exec将字符串中的python变量加载到functools这个模块的命名空间中
    exec(ENV["my_functools"], my_functools.__dict__)

    # 执行单条用例
    BaseCase().perform(testcase)

    # 断开连接
    db.close_db_connection()
