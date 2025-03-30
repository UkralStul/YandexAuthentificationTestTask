from pydantic import BaseModel, Field
import datetime
from typing import Optional

class AudioFileBase(BaseModel):
    filename: str = Field(..., description="User-provided filename for the audio")

class AudioFileCreate(AudioFileBase):
    pass

class AudioFileUpdate(BaseModel):
     filename: Optional[str] = None

class AudioFileInDBBase(AudioFileBase):
    id: int
    filepath: str
    owner_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class AudioFile(AudioFileInDBBase):
    pass

class AudioFileInfo(BaseModel):
    id: int
    filename: str
    filepath: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True