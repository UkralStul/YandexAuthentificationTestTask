from typing import Generator, Optional, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # Используем для извлечения токена из заголовка
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.core import security
from app.core.config import settings
from app.db import models
from app.db.session import get_db
from app.schemas.token import TokenPayload
from app.db import crud


reusable_oauth2 = HTTPBearer()

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(reusable_oauth2)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise credentials_exception

    raw_token_value = credentials.credentials

    if raw_token_value.lower().startswith("bearer "):
        token = raw_token_value.split(" ", 1)[1]
    else:
        token = raw_token_value

    if not token:
        raise credentials_exception

    token_data = security.verify_token(token)

    if not token_data or token_data.type != 'access':
        raise credentials_exception

    if token_data.sub is None:
        raise credentials_exception

    try:
        user_id_str = str(token_data.sub)

        user_id = int(user_id_str)
        user = await crud.get_user(db, user_id=user_id)
    except ValueError:
         raise credentials_exception

    if user is None:
         raise credentials_exception

    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    return current_user


async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user