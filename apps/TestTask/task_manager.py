# -*- coding: utf-8 -*-
"""
测试任务后台执行管理器
解决run_task卡死问题，实现异步执行和状态管理
"""
import asyncio
import uuid
import time
import traceback
from datetime import datetime
from typing import Dict, Optional, Any

from apps.TestTask.models import TestTask, TestRecord, TestReport
from apps.Suite.api import run_scenes
from apps.Suite.schemas import SuiteRunForm
import logging
import sys


class TaskStatus:
    """任务状态常量"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class BackgroundTaskManager:
    """后台任务管理器（使用当前事件循环，不跨线程）"""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

    async def create_task(self, task_id: int, env_id: int, tester: str) -> str:
        """创建新的后台任务并在当前事件循环中调度"""
        task_uuid = str(uuid.uuid4())

        async with self._lock:
            self.tasks[task_uuid] = {
                "task_id": task_id,
                "env_id": env_id,
                "tester": tester,
                "status": TaskStatus.PENDING,
                "progress": 0,
                "result": None,
                "error": None,
                "created_at": datetime.now(),
                "started_at": None,
                "completed_at": None,
                "record_id": None
            }

        asyncio.create_task(self._run_task_async(task_uuid))
        self.logger.info(f'任务创建: uuid={task_uuid} task_id={task_id} env_id={env_id} tester={tester}')
        return task_uuid

    async def _run_task_async(self, task_uuid: str):
        """异步执行任务"""
        task_info = self.tasks.get(task_uuid)
        if task_info is None:
            return

        # 获取任务信息
        task = await TestTask.get_or_none(id=task_info["task_id"])
        if not task:
            raise Exception("任务不存在")

        task_info["status"] = TaskStatus.RUNNING
        task_info["started_at"] = datetime.now()
        self.logger.info(f'任务开始: uuid={task_uuid} task_id={task_info["task_id"]}')

        # 创建测试记录
        record = await TestRecord.create(
            task_id=task_info["task_id"],
            env_id=task_info["env_id"],
            tester=task_info["tester"]
        )
        task_info["record_id"] = record.id

        # 初始化统计
        all_ = 0
        success = 0
        fail = 0
        error = 0
        start_time = time.time()
        result = []

        suites = await task.suite.all()
        total_suites = len(suites)
        self.logger.info(f'任务套件数: uuid={task_uuid} count={total_suites}')

        # 并发执行测试套件（关键改进）
        tasks = []
        for i, suite in enumerate(suites):
            # 创建异步任务
            suite_task = self._run_suite_with_timeout(
                suite.id, task_info["env_id"], i, total_suites, task_uuid
            )
            tasks.append(suite_task)

        # 等待所有套件执行完成（带超时）
        suite_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        for res in suite_results:
            if isinstance(res, Exception):
                error += 1
                self.logger.error(f"套件执行失败: {str(res)}")
            else:
                result.append(res)
                all_ += res.get('all', 0)
                success += res.get('success', 0)
                fail += res.get('fail', 0)
                error += res.get('error', 0)

        # 计算结果
        pass_rate = str(round((success / all_) * 100, 2)) if all_ > 0 else '0.0'
        if success == all_:
            status = '成功'
        elif error != 0:
            status = '错误'
        else:
            status = '失败'
        run_time = str(round(time.time() - start_time, 2)) + 's'

        # 更新记录
        record.all = all_
        record.success = success
        record.fail = fail
        record.error = error
        record.pass_rate = pass_rate
        record.run_time = run_time
        record.status = status
        await record.save()

        # 创建测试报告
        info = {
            "all": all_,
            "fail": fail,
            "error": error,
            "success": success,
            "results": result,
        }
        await TestReport.create(record=record, info=info)

        # 更新任务状态
        task_info["status"] = TaskStatus.COMPLETED
        task_info["result"] = {
            "status": status,
            "pass_rate": pass_rate,
            "run_time": run_time,
            "all": all_,
            "success": success,
            "fail": fail,
            "error": error
        }
        task_info["completed_at"] = datetime.now()
        task_info["progress"] = 100
        self.logger.info(f'任务完成: uuid={task_uuid} status={status} pass_rate={pass_rate} run_time={run_time}')

    async def _run_suite_with_timeout(self, suite_id: int, env_id: int, index: int, total: int, task_uuid: str):
        """执行单个套件（带超时）"""
        try:
            # 更新进度
            progress = int((index / total) * 100)
            self.tasks[task_uuid]["progress"] = progress

            # 执行套件（30秒超时）
            result = await asyncio.wait_for(
                run_scenes(SuiteRunForm(env=env_id, flow=suite_id)),
                timeout=30.0
            )

            self.logger.info(f"套件 {suite_id} 执行完成")
            return result

        except asyncio.TimeoutError:
            self.logger.error(f"套件 {suite_id} 执行超时")
            return {
                "all": 1,
                "success": 0,
                "fail": 0,
                "error": 1,
                "timeout": True
            }
        except Exception as e:
            self.logger.error(f"套件 {suite_id} 执行失败: {str(e)}")
            return {
                "all": 1,
                "success": 0,
                "fail": 0,
                "error": 1,
                "error_msg": str(e)
            }
    
    def get_task_status(self, task_uuid: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        return self.tasks.get(task_uuid)
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """获取所有任务"""
        return self.tasks.copy()
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """清理已完成的任务"""
        current_time = datetime.now()
        completed_tasks = [
            task_uuid for task_uuid, task_info in self.tasks.items()
            if task_info["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT]
            and task_info.get("completed_at") is not None
            and (current_time - task_info["completed_at"]).total_seconds() > max_age_hours * 3600
        ]
        
        for task_uuid in completed_tasks:
            del self.tasks[task_uuid]


# 全局任务管理器实例
task_manager = BackgroundTaskManager()


async def run_task_async(task_id: int, env_id: int, tester: str) -> str:
    """异步运行测试任务（基于当前事件循环）"""
    return await task_manager.create_task(task_id, env_id, tester)


def get_task_status(task_uuid: str) -> Optional[Dict[str, Any]]:
    """获取任务状态"""
    return task_manager.get_task_status(task_uuid)


def get_all_running_tasks() -> Dict[str, Dict[str, Any]]:
    """获取所有运行中的任务"""
    all_tasks = task_manager.get_all_tasks()
    return {
        task_uuid: task_info for task_uuid, task_info in all_tasks.items()
        if task_info["status"] in [TaskStatus.PENDING, TaskStatus.RUNNING]
    }
