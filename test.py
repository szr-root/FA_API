import datetime
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.triggers.cron import CronTrigger

# 配置 APScheduler
jobstores = {
    'default': RedisJobStore(host='localhost', port=6379, db=15, password='qwe123')
}
# 设置最大的执行线程数
executors = {
    'default': ThreadPoolExecutor(20)
}
# 设置最大的任务数
job_defaults = {
    'coalesce': False,
    'max_instances': 10
}
# 创建一个调度器
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)


def task1(name):
    print(f'执行间隔任务:{datetime.datetime.now()}----{name}')


def task2(name):
    print(f'执行(固定)时间点任务:{datetime.datetime.now()}----{name}')


def task3(name):
    print(f'执行周期任务:{datetime.datetime.now()}----{name}')


# 添加一个3s一次的间隔任务
scheduler.add_job(task1, id='interval_task', trigger=IntervalTrigger(seconds=3), args=['间隔3s的任务'])

# # 设置一个固定时间的任务
# scheduler.add_job(task2, id='date_task', trigger=DateTrigger(run_date='2024-12-24 14:50:00'), args=['固定时间点任务'])
#
# # 创建一个周期任务，周期间隔为5s
# scheduler.add_job(task3, id='cron_task',
#                   trigger=CronTrigger(year='*', month='*', day='*', hour='*', minute='*', second='5'),
#                   args=['周期任务'])

# 启动调度器
scheduler.start()

while True:
    time.sleep(1)
