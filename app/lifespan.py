from contextlib import asynccontextmanager
from fastapi import FastAPI
from models import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("START")
    yield
    print("FINISH")
