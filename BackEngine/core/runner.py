# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/01
# @File : runner.py

from BackEngine.core.basecase import db, BaseCase, my_functools
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
            "status": getattr(test, 'status', '成功'),
            "requests_header": getattr(test, 'requests_header', ''),
            "requests_body": getattr(test, 'request_body', ''),
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
            "status": getattr(test, 'status', '成功'),
            "requests_header": getattr(test, 'requests_header', ''),
            "requests_body": getattr(test, 'request_body', ''),
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
            "status": getattr(test, 'status', '成功'),
            "requests_header": getattr(test, 'requests_header', ''),
            "requests_body": getattr(test, 'request_body', ''),
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
            "status": '成功' if self.success == self.all else ('失败' if self.fail > 0 else '错误'),
        }


class TestRunner:
    def __init__(self, cases, env, env_object):
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
        self.env_object = env_object

    def run(self):
        """
        执行测试用例，优化数据库连接管理
        避免长时间占用连接资源
        """
        db_config = self.env_data.pop('DB')
        if db_config == '':
            db_config = [{
                "name": "local",
                "type": "mysql",
                "config": {"host": "127.0.0.1",
                           "port": 3306,
                           "user": "root",
                           "password": "songzhaoruizx"
                           }
            }]
        
        # 初始数据库连接
        db.init_connect(db_config)
        
        try:
            ENV = {}
            # 通过exec将字符串中的python变量加载到functools这个模块的命名空间中
            exec(self.env_data["global_func"], my_functools.__dict__)

            # 遍历所有测试用例
            for items in self.cases:
                ENV.clear()
                ENV.update(self.env_data)
                name = items["name"]  # 业务流名称
                print(f"开始执行测试套件: {name}")
                
                # 创建测试结果记录器
                result = TestResult(name=name, all=len(items["Cases"]))
                
                # 遍历测试集执行用例
                for i, testcase in enumerate(items["Cases"]):
                    try:
                        self.perform(testcase, result, ENV)
                    except Exception as e:
                        print(f"用例执行失败: {testcase.get('title', '未知用例')} - {str(e)}")
                        # 继续执行下一个用例，而不是中断整个套件
                        continue
                
                # 获取每条记录器的结果,保存起来
                self.result.append(result.get_result_info())
                
                # 每执行完一个套件，释放一些资源
                if hasattr(self, 'env_object') and self.env_object:
                    # 清理环境变量，避免内存累积
                    if hasattr(self.env_object, 'debug_global_variable'):
                        self.env_object.debug_global_variable.clear()
        
        finally:
            # 确保数据库连接被关闭
            try:
                db.close_db_connection()
            except Exception as e:
                print(f"关闭数据库连接时出错: {str(e)}")
        
        return self.result[0] if self.result else {"name": "空结果", "all": 0, "success": 0, "fail": 0, "error": 0, "cases": []}

    def perform(self, case, result, env):
        c = BaseCase()
        try:
            c.perform(case, env, self.env_object)
        except AssertionError as e:
            # print('用例断言失败')
            result.add_fail(c)
        except Exception as e:
            # print('用例执行错误')
            result.add_error(c, e)
        else:
            # print('用例执行通过')
            result.add_success(c)
            # return new_ENV


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
