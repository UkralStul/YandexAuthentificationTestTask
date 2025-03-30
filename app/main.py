from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Если нужен CORS для фронтенда
from contextlib import asynccontextmanager

from app.api import api_router # Импортируем наш главный роутер
from app.core.config import settings
from app.db.base import init_db
from app.db.session import engine # Импортируем движок


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    await init_db(engine)
    print("Database initialized.")
    yield
    print("Shutting down...")


app = FastAPI(
    title="Audio Upload Service",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Audio Upload Service API"}

