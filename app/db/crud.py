from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.orm import selectinload

from . import models
from app.schemas import user as user_schemas
from app.schemas import audio as audio_schemas
from typing import List, Optional

# User CRUD

async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def get_user_by_yandex_id(db: AsyncSession, yandex_id: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.yandex_id == yandex_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, *, user_in: user_schemas.UserCreate) -> models.User:
    db_user = models.User(
        yandex_id=user_in.yandex_id,
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        display_name=user_in.display_name,
        is_superuser=user_in.is_superuser,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(
    db: AsyncSession, *, db_user: models.User, user_in: user_schemas.UserUpdate
) -> models.User:
    update_data = user_in.model_dump(exclude_unset=True) # Pydantic v2
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def set_superuser_status(db: AsyncSession, user: models.User, is_superuser: bool) -> models.User:
    if user.is_superuser != is_superuser:
        user.is_superuser = is_superuser
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    user = await get_user(db, user_id)
    if user:
        await db.delete(user)
        await db.commit()
    return user


# AudioFile CRUD

async def create_audio_file(
    db: AsyncSession, *, file_in: audio_schemas.AudioFileCreate, owner_id: int, server_filepath: str
) -> models.AudioFile:
    db_file = models.AudioFile(
        filename=file_in.filename,
        filepath=server_filepath,
        owner_id=owner_id
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    return db_file

async def get_audio_files_by_owner(db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100) -> List[models.AudioFile]:
    result = await db.execute(
        select(models.AudioFile)
        .filter(models.AudioFile.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .order_by(models.AudioFile.created_at.desc())
    )
    return result.scalars().all()

async def get_audio_file(db: AsyncSession, file_id: int) -> Optional[models.AudioFile]:
    result = await db.execute(select(models.AudioFile).filter(models.AudioFile.id == file_id))
    return result.scalars().first()
