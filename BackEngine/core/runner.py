# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/01
# @File : runner.py

from BackEngine.core.basecase import db, ENV, BaseCase, my_functools
from BackEngine.core.dbclient import DBClient


class TestResult:
    """测试结果记录器,一个测试套件生成一个记录器"""

    def __init__(self, name, all):
        self.name = name
        self.all = all
        self.success = 0
        self.fail = 0
        self.error = 0
        self.cases = []
        # self.run_time = 0

    def add_success(self, test: BaseCase):
        """
        :param test: 用例对象
        :return:
        """
        # """执行成功"""
        self.success += 1
        info = {
            "name": getattr(test, 'title', ''),
            'method': getattr(test, 'method', ''),
            "url": getattr(test, 'url', ''),
            "status_code": getattr(test, 'status_code', ''),
            "status": "success",
            "request_header": getattr(test, 'request_header', ''),
            "request_body": getattr(test, 'request_body', ''),
            "run_time": getattr(test, 'run_time', ''),
            "response_header": getattr(test, 'response_header', ''),
            "response_body": getattr(test, 'response_body', ''),
            "log_data": getattr(test, 'log_data', ''),

        }
        self.cases.append(info)

    def add_fail(self, test):
        # """执行失败"""
        self.fail += 1
        info = {
            "name": getattr(test, 'title', ''),
            'method': getattr(test, 'method', ''),
            "url": getattr(test, 'url', ''),
            "status_code": getattr(test, 'status_code', ''),
            "status": "fail",
            "request_header": getattr(test, 'request_header', ''),
            "request_body": getattr(test, 'request_body', ''),
            "run_time": getattr(test, 'run_time', ''),
            "response_header": getattr(test, 'response_header', ''),
            "response_body": getattr(test, 'response_body', ''),
            "log_data": getattr(test, 'log_data', ''),

        }
        self.cases.append(info)

    def add_error(self, test: BaseCase, error):
        """

        :param test:
        :param error: 错误信息
        :return:
        """
        test.error_log("用例执行错误，错误信息如下")
        test.error_log(error)
        # 执行出错
        self.error += 1
        info = {
            "name": getattr(test, 'title', ''),
            'method': getattr(test, 'method', ''),
            "url": getattr(test, 'url', ''),
            "status_code": getattr(test, 'status_code', ''),
            "status": "error",
            "request_header": getattr(test, 'request_header', ''),
            "request_body": getattr(test, 'request_body', ''),
            "run_time": getattr(test, 'run_time', ''),
            "response_header": getattr(test, 'response_header', ''),
            "response_body": getattr(test, 'response_body', ''),
            "log_data": getattr(test, 'log_data', ''),

        }

        self.cases.append(info)

    def get_result_info(self):
        return {
            "name": self.name,
            "all": self.all,
            "success": self.success,
            "fail": self.fail,
            "error": self.error,
            "cases": self.cases,
            "status": 'success' if self.success == self.all else ('error' if self.error > 0 else 'fail'),
            # "run_time": self.run_time
        }


class TestRunner:
    def __init__(self, cases, env):
        """

        :param cases: 要执行的测试用例
        cases格式:[
            {
                "name":"业务流名称",
                "cases":[
                            {
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
                            },
                            ....
                    ]
            }
        ]
        :param env: 测试环境
        """
        self.cases = cases
        self.env_data = env
        self.result = []

    def run(self):
        # 初始数据库连接
        db.init_connect(self.env_data.pop('DB'))

        ENV.update(self.env_data)

        # 通过exec将字符串中的python变量加载到functools这个模块的命名空间中
        exec(ENV["global_func"], my_functools.__dict__)

        # 遍历所有测试用例
        for items in self.cases:
            ENV.clear()
            ENV.update(self.env_data)
            name = items["name"]  # 业务流名称
            # name = items["title"]  # 业务流名称
            print(name)
            # 创建测试结果记录器
            result = TestResult(name=name, all=len(items["Cases"]))
            # 遍历测试集执行用例
            for testcase in items["Cases"]:
                self.perform(testcase, result)
            # 获取每条记录器的结果,保存起来
            self.result.append(result.get_result_info())
        # 断开连接
        db.close_db_connection()
        return self.result, 'DEBUG'

    def perform(self, case, result):
        c = BaseCase()
        # run_time = 0
        try:
            c.perform(case)
        except AssertionError as e:
            # print('用例断言失败')
            result.add_fail(c)
            # result.run_time = run_time
        except Exception as e:
            # print('用例执行错误')
            result.add_error(c, e)
            # result.run_time = run_time
        else:
            # print('用例执行通过')
            result.add_success(c)
            # result.run_time = run_time


if __name__ == '__main__':
    # cases = [
    #     {
    #         "name": "登录",
    #         "cases": [
    #             {
    #                 "title": "登录成功用例0",
    #                 "interface":
    #                     {
    #                         "url": "/api/users/login/",
    #                         "method": "get",
    #                     },
    #                 "headers":
    #                     {
    #                         "Content-Type": "application/json",
    #                     },
    #                 "request": {
    #                     "params": {},
    #                     "json": {
    #                         "username": "john",
    #                         "password": "1111"
    #                     },
    #                 },
    #                 "setup_script": '',
    #                 "teardown_script": '',
    #             },
    #             {
    #                 "title": "登录成功用例",
    #                 "interface":
    #                     {
    #                         "url": "/api/users/login/",
    #                         "method": "post",
    #                     },
    #                 "headers":
    #                     {
    #                         "Content-Type": "application/json",
    #                     },
    #                 "request": {
    #                     "params": {},
    #                     "json": {
    #                         "username": "admin",
    #                         "password": "admin"
    #                     },
    #                 },
    #                 "setup_script": '',
    #                 "teardown_script": '',
    #             },
    #             {
    #                 "title": "登录成功用例2",
    #                 "interface":
    #                     {
    #                         "url": "/api/users/login/",
    #                         "method": "post",
    #                     },
    #                 "headers":
    #                     {
    #                         "Content-Type": "application/json",
    #                     },
    #                 "request": {
    #                     "params": {},
    #                     "json": {
    #                         "username": "john",
    #                         "password": "666666"
    #                     },
    #                 },
    #                 "setup_script": open('../setup_script.txt', 'r', encoding='utf-8').read(),
    #                 "teardown_script": open('../teardown_script.txt', 'r', encoding='utf-8').read(),
    #             },
    #         ]
    #     }
    # ]

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

    # res = TestRunner(cases, test_env_data).run()
    # print(res)
    db.init_connect(test_env_data.get('db'))
    #
    res1 = db.local.execute('select * from apitest.interFaceCases where id = 8')
    res2 = db.local.execute('select * from apitest.interFaceCases where id = 10')
    #
    envs = {"Envs": db.local.execute("select * from apitest.TestEnv where id = 4")}
    test_env_data.update(envs)

    # cases2 = [
    #     {'name': '登录', "cases": [res1, res2]}
    # ]

    cases2 = [
        {'name': '登录', "cases": [res1, res2]}
    ]

    res = TestRunner(cases2, test_env_data).run()
    print(res)
    # db.close_db_connection()
