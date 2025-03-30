import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from passlib.context import CryptContext # Пока не используется для паролей, но может пригодиться
from pydantic import ValidationError
import httpx

from app.core.config import settings, YANDEX_AUTH_URL, YANDEX_TOKEN_URL, YANDEX_USERINFO_URL
from app.schemas.token import TokenPayload

ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
SECRET_KEY = settings.SECRET_KEY

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        token_data = TokenPayload(**payload)

        now_utc = datetime.now(timezone.utc)
        exp_utc = datetime.fromtimestamp(token_data.exp, tz=timezone.utc)
        if exp_utc < now_utc:
             raise jwt.ExpiredSignatureError("Token has expired")

        return token_data

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidSignatureError:
        return None
    except jwt.PyJWTError as e:
        return None
    except ValidationError as e:
         return None

# Yandex OAuth Functions

def get_yandex_authorize_url() -> str:
    params = {
        "response_type": "code",
        "client_id": settings.YANDEX_CLIENT_ID,
        "redirect_uri": str(settings.YANDEX_REDIRECT_URI),
    }
    request = httpx.Request('GET', YANDEX_AUTH_URL, params=params)
    return str(request.url)

async def exchange_yandex_code_for_token(code: str) -> Optional[str]:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.YANDEX_CLIENT_ID,
        "client_secret": settings.YANDEX_CLIENT_SECRET,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(YANDEX_TOKEN_URL, data=data)
            response.raise_for_status()
            token_data = response.json()
            return token_data.get("access_token")
        except httpx.HTTPStatusError as e:
            print(f"Error exchanging Yandex code: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during Yandex token exchange: {e}")
            return None


async def get_yandex_user_info(yandex_access_token: str) -> Optional[Dict[str, Any]]:
    headers = {"Authorization": f"OAuth {yandex_access_token}"}
    params = {"format": "json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(YANDEX_USERINFO_URL, headers=headers, params=params)
            response.raise_for_status()
            user_info = response.json()
            if "id" not in user_info:
                print(f"Yandex user info response missing 'id': {user_info}")
                return None
            return user_info
        except httpx.HTTPStatusError as e:
            print(f"Error getting Yandex user info: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during Yandex user info fetch: {e}")
            return None