from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api import deps
from app.db import crud, models
from app.schemas import user as user_schemas

router = APIRouter()

@router.get("/me", summary="Get current user info", response_model=user_schemas.User)
async def read_users_me(
    current_user: models.User = Depends(deps.get_current_active_user),
):
    return current_user

@router.patch("/me", summary="Update current user info", response_model=user_schemas.User)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: user_schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    user = await crud.update_user(db=db, db_user=current_user, user_in=user_in)
    return user

@router.delete(
    "/{user_id}",
    summary="Delete a user (Superuser only)",
    response_model=user_schemas.User,
    dependencies=[Depends(deps.get_current_active_superuser)]
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_superuser: models.User = Depends(deps.get_current_active_superuser)
):

    user_to_delete = await crud.get_user(db, user_id=user_id)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this ID does not exist in the system",
        )
    deleted_user = await crud.delete_user(db=db, user_id=user_id)
    return user_to_delete