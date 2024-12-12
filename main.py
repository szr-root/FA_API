import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from common import settings

from apps.users.api import router as user_router
from apps.projects.api import router as pro_router
from apps.Interface.api import router as interface_router

app = FastAPI(title='FastApi学习项目', summary='这个是学习项目的接口文档', version='0.0.1')

app.include_router(user_router)
app.include_router(pro_router)
app.include_router(interface_router)

register_tortoise(app, config=settings.TORTOISE_ORM, modules={'models': ['models']})

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
