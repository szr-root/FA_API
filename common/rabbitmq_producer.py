# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/20
# @File : rabbitmq_producer.py
import json

import pika
from .settings import MQ_CONFIG


class MQProducer:
    def __init__(self):
        # 连接到rabbitmq服务器
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=MQ_CONFIG.get('host'), port=MQ_CONFIG.get('port'))
        )
        self.channel = self.connection.channel()

        # 声明一个队列
        self.channel.queue_declare(queue=MQ_CONFIG.get('queue'))

    def send_test_task(self, env_config, run_suite):
        # 发送消息
        data = {
            "env_config": env_config,
            "run_suite": run_suite
        }
        msg = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.channel.basic_publish(exchange='', routing_key=MQ_CONFIG.get('queue'), body=msg)

    def __del__(self):
        # 关闭连接
        self.connection.close()


# 单例
mq = MQProducer()
