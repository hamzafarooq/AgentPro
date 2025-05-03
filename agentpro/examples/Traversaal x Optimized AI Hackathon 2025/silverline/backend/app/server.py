from config import CONFIG
from fastapi import FastAPI
from app.routes.routes import MAIN_ROUTER
from fastapi.middleware import Middleware
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.utils.base_schema.base_schema import GLOBAL_RESPONSES
from app.db.prisma_client import connect_prisma, disconnect_prisma
from app.utils.err.exception_handlers import register_error_handlers
from app.middleware.middleware_handler import register_middleware_handler


def init_routers(app_: FastAPI) -> None:
    app_.include_router(MAIN_ROUTER)


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ]
    return middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_prisma()
    # await cron_job()
    yield
    await disconnect_prisma()


def create_app() -> FastAPI:
    app_ = FastAPI(
        title=CONFIG.app_name,
        description=CONFIG.description,
        version=CONFIG.version,
        middleware=make_middleware(),
        lifespan=lifespan,
        responses=GLOBAL_RESPONSES,
        docs_url="/docs",
        redoc_url="/redoc",
        swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"}
    )
    # Initialize app state for call data
    app_.state.call_data = {}
    
    init_routers(app_=app_)
    register_error_handlers(app=app_)
    register_middleware_handler(app=app_)
    return app_


app = create_app()