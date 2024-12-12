# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/10/31
# @File : dbclient.py
import pymssql as pymssql
import pymysql


class DBBase:
    cursor = None
    conn = None

    def execute(self, sql, args=None):
        """执行sql语句,返回单条数据"""
        try:
            self.cursor.execute(sql, args)
            return self.cursor.fetchone()
        except Exception as e:
            raise e

    def execute_all(self, sql, args=None):
        """执行sql语句,返回所有数据"""
        try:
            self.cursor.execute(sql, args)
            return self.cursor.fetchall()
        except Exception as e:
            raise e

    def close(self):
        """关闭数据库连接"""
        self.cursor.close()
        self.conn.close()


class MySqlDB(DBBase):
    """mysql数据库操作类"""

    def __init__(self, db_config):
        """初始化数据库连接"""
        self.conn = pymysql.connect(**db_config, autocommit=True)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)


class SqlServerDB(DBBase):
    """sqlserver数据库操作类"""

    def __init__(self, db_config):
        """初始化数据库连接"""
        self.conn = pymssql.connect(**db_config, autocommit=True)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)


class OracleDB(DBBase):
    """oracle数据库操作类"""
    pass


class DBClient:
    """数据库连接对象"""

    # 创建时不连接，不定义init方法
    def init_connect(self, dbs):
        """ 初始化数据库连接"""
        if isinstance(dbs, dict):
            # 单个数据库配置
            self.create_db_connection(dbs)

        elif isinstance(dbs, list):
            # 多个数据库配置
            for db in dbs:
                self.create_db_connection(db)
        else:
            raise ValueError("数据库配置不正确")

    def create_db_connection(self, db):
        """创建数据库连接"""

        if not (db.get('name') and db.get('type') and db.get('config')):
            raise TypeError("数据库配置格式错误")

        if db.get('type') == 'mysql':
            # 连接mysql数据库
            obj = MySqlDB(db.get('config'))
            setattr(self, db.get('name'), obj)

        elif db.get('type') == 'sqlserver':
            # 连接sqlserver数据库
            pass
        elif db.get('type') == 'oracle':
            # 连接oracle数据库
            pass
        else:
            raise ValueError("数据库配置有问题，或该类型类型不支持，现目前只支持mysql，sqlserver")

    def close_db_connection(self):
        """关闭数据库连接"""
        for db in self.__dict__:
            if isinstance(self.__dict__[db], DBBase):
                self.__dict__[db].close()


if __name__ == '__main__':
    items = [{
        "name": "local",
        "type": "mysql",
        "config": {"host": "127.0.0.1",
                   "port": 3306,
                   "user": "root",
                   "password": "songzhaoruizx"
                   }
    }]
    db_client = DBClient()
    db_client.init_connect(items)

    res = db_client.local.execute("select * from apitest.auth_user")
    print(res)

    db_client.close_db_connection()
