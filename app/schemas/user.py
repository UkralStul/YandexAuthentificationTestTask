from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    is_superuser: bool = False


class UserCreate(UserBase):
    yandex_id: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None


class UserInDBBase(UserBase):
    id: int
    yandex_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    pass