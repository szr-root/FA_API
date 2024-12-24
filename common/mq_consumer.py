# -*- coding: utf-8 -*-
# @Author : John
# @Time : 2024/11/20
# @File : mq_consumer.py
import json
import pika
from BackEngine.core.runner import TestRunner
from common.settings import MQ_CONFIG
from common import db_client


class MQConsumer:
    def __init__(self):
        # 连接到rabbitmq服务器
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=MQ_CONFIG.get('host'), port=MQ_CONFIG.get('port'))
        )
        self.channel = self.connection.channel()

        # 设置回调函数，处理接收到的消息
        self.channel.basic_consume(queue=MQ_CONFIG.get('queue'), on_message_callback=self.run_test, auto_ack=True)

    def run_test(self, channel, method, properties, body):
        try:
            datas = json.loads(body.decode())
            env_config = datas.get('env_config')
            run_suite = datas.get('run_suite')
            runner = TestRunner(env_config, run_suite)
            result = runner.run()

            db = db_client.DB()

            if run_suite.get('task_record_id'):
                self.save_task_result(run_suite.get('task_record_id'), result, db)
                self.save_suite_result(run_suite.get("suite_record_id"), result, db)

            elif run_suite.get('suite_record_id'):
                self.save_suite_result(run_suite.get('suite_record_id'), result, db)

            else:
                if len(result['run_cases']):
                    self.save_case_result(result['run_cases'][0], db)
                elif len(result['no_run_cases']):
                    self.save_case_result(result['no_run_cases'][0], db)

            db.close()
        except Exception as e:
            print("节点执行用例报错", e)

    def save_task_result(self, task_record_id, result, db):
        """保存测试任务执行结果"""
        # 通过任务执行记录id
        sql = "SELECT * FROM task_run_records WHERE id=%s"
        db.execute(sql, (task_record_id,))
        # 获取查询结果
        task_data = db.fetch_one()
        # 准备sql
        sql = """
        UPDATE task_run_records SET 
        status=%s,
        run_all = %s,
        no_run = %s,
        success = %s,
        fail =%s,
        error = %s,
        skip = %s
        WHERE id=%s
        """
        params = {
            'run_all': task_data['run_all'] + len(result.get('run_cases')),
            'no_run': task_data['no_run'] + result.get('no_run', 0),
            'success': task_data['success'] + result.get('success', 0),
            'fail': task_data['fail'] + result.get('fail', 0),
            'error': task_data['error'] + result.get('error', 0),
            'skip': task_data['skip'] + result.get('skip', 0),
        }
        if task_data['all'] == params['run_all'] + params['no_run']:
            params["status"] = "执行完成"
        else:
            params["status"] = "执行中"

        res = db.execute(sql, (params.get('status'), params.get('run_all'), params.get('no_run'),
                               params.get('success'), params.get('fail'), params.get('error'),
                               params.get('skip'), task_record_id)
                         )
        print("执行任务记录的数据修改结果", res)

    def save_suite_result(self, suite_record_id, result, db):
        """保存测试套件执行结果"""
        # 准备sql
        sql = """
        UPDATE suite_run_records SET 
        status=%s,
        run_all = %s,
        no_run = %s,
        success = %s,
        fail =%s,
        error = %s,
        skip = %s,
        duration = %s,
        suite_log =%s,
        pass_rate = %s
        WHERE id=%s
        """
        pass_rate = 0
        if result['all'] > 0:
            # TODO
            # pass_rate = round(result.get('success') / result.get('run_all') * 100, 2)
            pass_rate = round((result.get('success', 0) + result.get('skip', 0)) / result.get('all') * 100, 2)
        # 准备参数
        params = {
            'status': '执行完成',
            'run_all': len(result.get('run_cases')) if len(result.get('run_cases')) else 0,
            'no_run': result.get('no_run', 0),
            'success': result.get('success'),
            'fail': result.get('fail'),
            'error': result.get('error'),
            'skip': result.get('skip'),
            'duration': result.get('duration'),
            'suite_log': json.dumps(result.get('suite_log'), ensure_ascii=False),
            'pass_rate': pass_rate,
        }

        res = db.execute(sql, (params.get('status'), params.get('run_all'), params.get('no_run'), params.get('success'),
                               params.get('fail'), params.get('error'), params.get('skip'), params.get('duration'),
                               params.get('suite_log'), params.get('pass_rate'), suite_record_id))

        print("套件执行sql结果", res)

        # 保存套件中用例执行结果
        for case_result in result.get('run_cases'):
            self.save_case_result(case_result, db)
        for case_result in result.get('no_run_cases'):
            self.save_case_result(case_result, db)

    def save_case_result(self, result, db):
        """保存测试用例执行结果"""
        # 准备sql
        sql = 'UPDATE case_run_records SET state=%s,run_info=%s WHERE id=%s'
        params = (result.get('state'), json.dumps(result, ensure_ascii=False), result.get('record_id'))
        if result.get('suite_record_id'):
            sql = 'UPDATE case_run_records SET state=%s,run_info=%s,suite_run_record_id=%s WHERE id=%s'
            params = (result.get('state'), json.dumps(result, ensure_ascii=False), result.get('suite_record_id'),
                      result.get('record_id'))
        # 执行sql
        res = db.execute(sql, params)
        print(f"用例{result.get('id')}执行结果:", res)

    def main(self):
        # 启动执行，等待任务
        self.channel.start_consuming()


if __name__ == '__main__':
    c1 = MQConsumer()
    c1.main()
