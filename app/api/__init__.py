from fastapi import APIRouter

from app.api.endpoints import auth, users, audio

api_router = APIRouter()

# Подключаем роутеры с префиксами
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(audio.router, prefix="/audio", tags=["Audio"])