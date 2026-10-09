
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from asgi_correlation_id import CorrelationIdMiddleware

import logging

from socmedAPI.routers.post import router as post_router
from socmedAPI.database import database
from socmedAPI.logging_conf import configure_logging
from socmedAPI.routers.user import router as user_router


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting up the application...")
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan, title="Social Media API", description="A simple social media API built with FastAPI and SQLite", version="1.0.0")

app.add_middleware(CorrelationIdMiddleware)

app.include_router(post_router)
app.include_router(user_router)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)