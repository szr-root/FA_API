# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/22
# @File : db_client.py

"""
pip install pika
pip install playwright
playwright install
pip install pymysql
"""
from common.settings import DATABASE
import pymysql


class DB:
    def __init__(self):
        # 连接数据库
        self.conn = pymysql.connect(
            host=DATABASE['host'],
            port=DATABASE['port'],
            user=DATABASE['user'],
            password=DATABASE['password'],
            database=DATABASE['database'],
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )

        # 创建游标
        self.cursor = self.conn.cursor()

    def execute(self, sql, args=None):
        result = self.cursor.execute(sql, args)
        return result

    def fetch_one(self):
        return self.cursor.fetchone()

    def fetch_all(self):
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()
