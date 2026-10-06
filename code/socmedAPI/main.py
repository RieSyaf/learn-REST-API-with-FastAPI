from contextlib import asynccontextmanager
from fastapi import FastAPI

from socmedAPI.routers.post import router as post_router
from socmedAPI.database import database



@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan, title="Social Media API", description="A simple social media API built with FastAPI and SQLite", version="1.0.0")

app.include_router(post_router)
