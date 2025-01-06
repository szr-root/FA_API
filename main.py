from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from common import settings

from apps.users.api import router as user_router
from apps.projects.api import router as pro_router
from apps.projects.api import file_router
from apps.Interface.api import router as interface_router
from apps.Suite.api import router as suite_router
from apps.TestTask.api import router as task_router
from apps.Crontab.api import router as cron_router, scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时调用
    if not scheduler.running:
        scheduler.start()
        print("Scheduler started")
    yield
    # 关闭时调用
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler stopped")


app = FastAPI(title='FastApi学习项目', summary='这个是学习项目的接口文档', version='0.0.1', lifespan=lifespan)

app.include_router(user_router)
app.include_router(pro_router)
app.include_router(file_router)
app.include_router(interface_router)
app.include_router(suite_router)
app.include_router(task_router)
app.include_router(cron_router)

register_tortoise(app, config=settings.TORTOISE_ORM, modules={'models': ['models']})

origins = ['http://192.168.31.203:8080','http://127.0.0.1:8080',"http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    # uvicorn.run(app, host="172.20.20.54", port=8000)
    uvicorn.run(app, host="192.168.31.203", port=8000)
