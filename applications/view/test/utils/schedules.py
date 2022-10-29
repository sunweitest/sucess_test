from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from flask_apscheduler import APScheduler as _BaseAPScheduler

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


# 重写APScheduler，实现上下文管理机制，小优化功能也可以不要。对于任务函数涉及数据库操作有用
class APScheduler(_BaseAPScheduler):
    def run_job(self, id, jobstore=None):
        with self.app.app_context():
            super().run_job(id=id, jobstore=jobstore)


# 定时器配置项
class SchedulerConfig(object):
    # 持久化配置，数据持久化至MongoDB
    SCHEDULER_JOBSTORES = {'default': SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")}
    # 线程池配置，最大20个线程
    SCHEDULER_EXECUTORS = {'default': ThreadPoolExecutor(20)}
    # 调度开关开启
    SCHEDULER_API_ENABLED = True
    # 设置容错时间为 1小时
    SCHEDULER_JOB_DEFAULTS = {'misfire_grace_time':3600}
    # 配置时区
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'


scheduler = APScheduler()