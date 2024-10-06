from pydantic_settings import BaseSettings
from pydantic import BaseModel, validator


class Settings(BaseSettings):
    SPLIT_FILE_TYPES: str
    CUE_SPLIT_OUT_DIR: str
    DB_DIR: str
    LOSSLESS_IN_DIR: str
    MP3_OUT_DIR: str
    DEV_BOXES: str
    FFMPEG: str
    FFPROBE: str

    ROOT_DIR: str

    SPLIT_FILE_TYPES: str
    FLAC_VOLUME: str
    MP3_VOLUME: str
    SPLIT_VOLUME: str
    DB_VOLUME: str
    FLAC_RENAME_STR: str

    DB_FILENAME: str
    DATABASE_FILE: str

    class Config:
        env_file = '/Users/ad/Projects/music_service/.env-docker'

    @validator('DATABASE_FILE', pre=True, always=True)
    def set_DATABASE_FILE(cls, value, values):
        # Access the original value from 'foo'
        DB_FILENAME = values.get('DB_FILENAME', '')
        return f"/db/{DB_FILENAME}"
