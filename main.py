import uvicorn
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from common import settings
from contextlib import asynccontextmanager

from apps.users.api import router as user_router
from apps.projects.api import router as pro_router
from apps.projects.api import file_router
from apps.Interface.api import router as interface_router
from apps.Suite.api import router as suite_router
from apps.TestTask.api import router as task_router
from apps.Crontab.api import router as cron_router, scheduler, init_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时调用
    if not scheduler.running:
        await init_scheduler()
        print("Scheduler started")
    yield
    # 关闭时调用
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler stopped")


app = FastAPI(title='FastApi学习项目', summary='这个是学习项目的接口文档', version='0.0.1',
              docs_url=None,
              redoc_url=None,  # 设置 ReDoc 文档的路径
              lifespan=lifespan)

app.include_router(user_router)
app.include_router(pro_router)
app.include_router(file_router)
app.include_router(interface_router)
app.include_router(suite_router)
app.include_router(task_router)
app.include_router(cron_router)

register_tortoise(app, config=settings.TORTOISE_ORM, modules={'models': ['models']})

origins = [
    'http://127.0.0.1:8080',
    'http://localhost:8080',
    'http://localhost:5173',
    'http://localhost:5188',
    'http://localhost:5175',
    "https://testapi-1301806088.cos.ap-chengdu.myqcloud.com",
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="new swagger",
        # oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url='/static/swagger/swagger-ui-bundle.js',
        swagger_css_url='/static/swagger/swagger-ui.css',
        swagger_favicon_url='/static/swagger/img.png',
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/swagger/redoc.standalone.js",
    )


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
