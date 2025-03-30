import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api import deps
from app.db import crud, models
from app.schemas import audio as audio_schemas
from app.core.config import settings

router = APIRouter()

@router.post("/upload", summary="Upload an audio file", response_model=audio_schemas.AudioFile)
async def upload_audio(
    *,
    db: AsyncSession = Depends(deps.get_db),
    filename: str = Form(..., description="Desired filename for the audio"),
    file: UploadFile = File(..., description="Audio file to upload"),
    current_user: models.User = Depends(deps.get_current_active_user),
):

    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only audio files are allowed.",
        )

    _, file_extension = os.path.splitext(file.filename or "unknown.mp3")
    server_filename = f"{uuid.uuid4()}{file_extension}"
    upload_dir = Path(settings.UPLOADS_DIR)
    file_path = upload_dir / server_filename
    file_path_str = str(file_path.relative_to(Path('.').resolve()))

    try:
        with open(file_path, "wb") as buffer:
             shutil.copyfileobj(file.file, buffer)

    except Exception as e:
        if file_path.exists():
             file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {e}",
        )
    finally:
        await file.close()

    audio_in = audio_schemas.AudioFileCreate(filename=filename)
    db_audio = await crud.create_audio_file(
        db=db, file_in=audio_in, owner_id=current_user.id, server_filepath=file_path_str
    )

    return db_audio


@router.get("", summary="Get list of user's audio files", response_model=List[audio_schemas.AudioFileInfo])
async def get_user_audio_files(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    audio_files = await crud.get_audio_files_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return [audio_schemas.AudioFileInfo.model_validate(f) for f in audio_files] # Pydantic v2