import os

from pydantic_settings import BaseSettings
from pydantic import validator
from constants import DB_FILENAME, ROOT_DIR


class Settings(BaseSettings):
    # Base folder for  recursive cuefile search
    SPLIT_SEARCH_DIR: str

    # location of the tracking database
    DB_DIR: str

    # source lossless folder
    LOSSLESS_IN_DIR: str

    # folder where converted mp3's end up
    MP3_OUT_DIR: str

    # source video folder
    VIDEO_DIR: str

    # network names of the local development machine running this package
    LOCAL_NAMES: str

    # ffmpeg command
    FFMPEG: str

    # ffprobe command
    FFPROBE: str

    # lossless docker volume
    FLAC_VOLUME: str

    # mp3 docker output volume
    MP3_VOLUME: str

    # default location to search for image/cue files to split
    SPLIT_VOLUME: str

    # database docker volume
    DB_VOLUME: str

    # docker video volume
    VIDEO_VOLUME: str

    # full path of the database file
    DATABASE_FILE: str

    class Config:
        if os.environ.get('LOCAL') == 'true':
            env_file = '.env-local'
        else:
            env_file = os.path.join(ROOT_DIR, 'app', '.env-docker')
        print(env_file, os.path.exists(env_file))
    @validator('DATABASE_FILE', pre=True, always=True)
    def set_database_full_path(cls, value, values):
        return f"{values.get('DB_DIR')}/{DB_FILENAME}"
