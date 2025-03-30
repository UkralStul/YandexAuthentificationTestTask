from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.api import deps
from app.core import security
from app.core.config import settings
from app.db import crud
from app.schemas import token as token_schemas
from app.schemas import user as user_schemas

router = APIRouter()

@router.get("/yandex/login", summary="Redirect to Yandex for authentication")
async def login_via_yandex():
    authorize_url = security.get_yandex_authorize_url()
    return RedirectResponse(authorize_url)

@router.get("/yandex/callback", summary="Handle Yandex OAuth callback", response_model=token_schemas.Token)
async def handle_yandex_callback(
    code: str,
    db: AsyncSession = Depends(deps.get_db)
):
    yandex_token = await security.exchange_yandex_code_for_token(code)
    if not yandex_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not exchange Yandex code for token",
        )

    yandex_user_info = await security.get_yandex_user_info(yandex_token)
    if not yandex_user_info or "id" not in yandex_user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not fetch user info from Yandex",
        )

    yandex_id = yandex_user_info["id"]
    email = yandex_user_info.get("default_email")
    first_name = yandex_user_info.get("first_name")
    last_name = yandex_user_info.get("last_name")
    display_name = yandex_user_info.get("display_name")

    user = await crud.get_user_by_yandex_id(db, yandex_id=yandex_id)

    is_superuser = (str(yandex_id) == settings.FIRST_SUPERUSER_YANDEX_ID)

    if user:
        if user.is_superuser != is_superuser:
            user = await crud.set_superuser_status(db, user=user, is_superuser=is_superuser)
    else:
        user_in = user_schemas.UserCreate(
            yandex_id=yandex_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            is_superuser=is_superuser
        )
        user = await crud.create_user(db=db, user_in=user_in)

    access_token = security.create_access_token(subject=user.id)
    refresh_token = security.create_refresh_token(subject=user.id)

    return token_schemas.Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/token/refresh", summary="Refresh access token", response_model=token_schemas.Token)
async def refresh_access_token(
    refresh_request: token_schemas.RefreshTokenRequest,
    db: AsyncSession = Depends(deps.get_db)
):
    token_data = security.verify_token(refresh_request.refresh_token)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token_data or token_data.type != 'refresh':
        raise credentials_exception

    if token_data.sub is None:
         raise credentials_exception

    try:
        user_id = int(token_data.sub)
    except ValueError:
        raise credentials_exception

    user = await crud.get_user(db, user_id=user_id)
    if not user:
        raise credentials_exception

    new_access_token = security.create_access_token(subject=user.id)
    new_refresh_token = security.create_refresh_token(subject=user.id)

    return token_schemas.Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )