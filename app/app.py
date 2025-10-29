from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiohttp
from fastapi import FastAPI
from starlette.requests import Request

from .modules.config import config
from .modules.db import Database
from .modules.auth.routes import router as auth_router


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


app = FastAPI(
    lifespan=lifespan,
)

app.include_router(
    auth_router,
    prefix='/v1',
)
