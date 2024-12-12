# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/06/19
# @File : basecase.py

import re
import requests
# 导入内置的测试工具函数
from BackEngine.core import testtools as my_functools
from jsonpath import jsonpath
from BackEngine.core.caselog import CaseLogHandel

from BackEngine.core.dbclient import DBClient

# 定义一个全局变量用来保存测试执行环境的数据
ENV = {}
# 创建一个数据库连接对象
db = DBClient()


# 创建一个数据库连接对象
# db = DBClient()


class BaseCase(CaseLogHandel):
    """用例执行的基本父类"""

    def __run_script(self, data):
        """专门执行前后置脚本的函数"""
        # 在前后置脚本的执行环境中内置一些变量
        test = self
        global_val = ENV.get('Envs', {})
        print = self.print_log
        # 获取用例的前置脚本
        setup_script = data.get('setup_script')
        # 使用执行器函数执行python的脚步代码
        exec(setup_script)
        # 接受传进来的响应结果
        response = yield
        teardown_script = data.get('teardown_script')
        exec(teardown_script)
        yield

    def __setup_script(self, data):
        """
        脚本执行前
        :param data:
        :return:
        """
        # 使用脚本执行器函数创建一个生成器对象
        self.script_hook = self.__run_script(data)
        # 执行前置脚步（执行生成器中的代码）
        next(self.script_hook)

    def __teardown_script(self, data, response):
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

    def __handler_requests_data(self, data):
        """处理请求数据的方法"""
        request_data = {}
        # 1、处理请求的url
        request_data["method"] = data['interface']['method']
        url = data['interface']['url']
        if not url.startswith('http'):
            # 和base_url进行拼接
            url = ENV.get('base_url') + url
        request_data["url"] = url
        self.url = url
        self.method = data['interface']['method']
        # 2、处理请求的headers
        # 获取全局请求头
        headers: dict = ENV.get('headers')
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
        if headers.get('Content-Type') == 'application/json':
            request_data['json'] = request.get('json')
            self.request_body = request.get('json')
        elif headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            request_data['data'] = request.get('data')
            self.request_body = request.get('data')
        elif 'multipart/form-data' in headers.get('Content-Type'):
            request_data['files'] = request.get('files')
            self.request_body = request.get('files')
        # 替换用例中的变量
        request_data = self.replace_data(request_data)

        return request_data

    def replace_data(self, data):
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
            value = ENV.get('Envs').get(key)
            # 将匹配到的内容中的变量替换为全局变量中的值
            data = data.replace(match.group(), str(value))

        return eval(data)

    def __send_request(self, data):
        """
        发送请求的方法
        :param data:
        :return:
        """
        # 处理用例的请求数据(替换请求参数中的变量，将数据转换为requests发送请求所需要的格式)
        request_data = self.__handler_requests_data(data)
        self.info_log(request_data)
        # 发送请求
        response = requests.request(**request_data)
        # self.request_headers = response.request.headers
        # self.response_headers = response.headers
        # self.response_body = response.text
        # self.request_body = response.request.body
        self.status_code = response.status_code
        self.info_log('请求地址', response.url)
        self.info_log('请求方式', response.request.method)
        self.info_log('请求头', response.request.headers)
        self.info_log('请求体', response.request.body)
        self.info_log('响应头', response.headers)
        self.info_log('响应体', response.text)
        self.info_log(response.text)
        # 返回响应对象

        return response

    def perform(self, data):
        """
        执行单条用例的入口方法
        :param data:
        :return:
        """
        self.title = data.get('title')
        self.data = data
        self.info_log("===开始执行用例:", self.title, '===')
        # 执行前置脚本
        self.__setup_script(data)
        # 发送请求
        response = self.__send_request(data)
        # 执行后置脚本
        self.__teardown_script(data, response)

    def save_global_variable(self, name, value):
        """
        保存测试运行环境的变量
        :param data:
        :return:
        """
        self.info_log("设置全局变量:", name, value)
        ENV['Envs'][name] = value

    def del_global_variable(self, name):
        """
        删除测试运行环境的变量
        :param name:
        :return:
        """
        self.info_log("删除全局变量:", name)
        del ENV['Envs'][name]

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
    def assertion(self, assert_list: list):
        """
        :param method: 断言的方法
        :param expected: 预期结果
        :param actual: 实际结果的值
        :return:
        """
        # self.info_log(assert_list)
        method_map = {
            '相等': lambda x, y: x == y,
            '不相等': lambda x, y: x != y,
            '大于': lambda x, y: x > y,
            '大于等于': lambda x, y: x >= y,
            '小于': lambda x, y: x < y,
            '小于等于': lambda x, y: x <= y,
            '不包含': lambda x, y: x not in y,
            '包含': lambda x, y: x in y,
        }
        for item in assert_list:
            assert_func = method_map.get(item['method'])
            if assert_func is None:
                self.info_log("不支持的断言方法：", item['method'])
                return
            else:
                self.debug_log("断言比较方法为：", item['method'])
                self.debug_log("预期结果:", item['expected'])
                self.debug_log("实际结果:", item['actual'])
            try:
                assert assert_func(item['expected'], item['actual'])
            except AssertionError:
                self.warning_log("断言失败，预期结果为：", item['expected'], "实际结果为：", item['actual'])
                raise AssertionError("断言失败，预期结果为：{},实际结果为：{}".format(item['expected'], item['actual']))
            else:
                self.info_log("断言成功，预期结果为：", item['expected'], "实际结果为：", item['actual'])


if __name__ == '__main__':
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
