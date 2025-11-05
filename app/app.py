import importlib
import pkgutil
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import aiohttp
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from middleware.auth import AuthMiddleware
from modules.config import config
from modules.db import Database



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with (
        db_client(app),
        http_client(app),
        app_config(app)
    ):
        yield


@asynccontextmanager
async def app_config(app: FastAPI) -> AsyncGenerator[None, None]:
    app_config = getattr(app.state, 'config', None)

    if app_config is None:
        app.state.config = config
    try:
        yield
    finally:
        pass


@asynccontextmanager
async def db_client(app: FastAPI) -> AsyncGenerator[None, None]:
    db_client = getattr(app.state, 'db_client', None)
    if db_client is None:
        db_client = Database(config.get('psql'))
        app.state.db_client = db_client

    await db_client.connect()
    try:
        yield
    finally:
        await db_client.disconnect()


@asynccontextmanager
async def http_client(app: FastAPI) -> AsyncGenerator[None, None]:
    http_client = getattr(app.state, 'http', None)

    if http_client is None:
        http_client = aiohttp.ClientSession()
        app.state.http = http_client

    try:
        yield
    finally:
        await http_client.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    AuthMiddleware,
    exclude_from_auth=[
        '/v1/auth/signup',
        '/v1/auth/signin',
        '/docs',
        '/openapi.json',
        '/redoc',
    ]
)

app.add_middleware(
    SessionMiddleware,
    secret_key=config.get('auth', {}).get('session_secret', 'change-me-in-production'),
    same_site='lax',
    max_age=config.get('auth', {}).get('session_max_age', 3600),
    https_only=False,
)


for _, m_name, ispkg in pkgutil.iter_modules([str(Path(__file__).parent / 'modules')]):
    if not ispkg:
        continue

    module = importlib.import_module(f'modules.{m_name}.routes')
    if hasattr(module, 'router'):
        for route in module.router.routes:
            if not getattr(route, 'response_model_exclude_unset', False):
                route.response_model_exclude_unset = True

        app.include_router(module.router, prefix='/v1')
