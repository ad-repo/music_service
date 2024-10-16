import json
import logging
import os
import sqlite3
import subprocess
from typing import Optional, Dict, Any

from helpers import CaseInsensitiveDict, NoMetadataException
from settings import Settings

env_settings = Settings()
for setting in env_settings:
    print(setting)

def create_db():
    conn = sqlite3.connect(env_settings.DATABASE_FILE)
    cursor = conn.cursor()

    # SQL command to create the 'track' table if it does not exist
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS track (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist TEXT,
        title TEXT,
        album TEXT,
        bitrate INTEGER,
        genre TEXT,
        year INTEGER,
        rating INTEGER,
        duration REAL,
        flac_filename TEXT UNIQUE,
        mp3_filename TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''

    logging.info(create_table_query)
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()


class Track:
    """
    Track class is a music track with 2 possible versions flac with and mp3
    """

    def __init__(self, **kwargs: Optional[Dict[str, Any]]):
        self.artist: Optional[str] = kwargs.get('artist')
        self.title: Optional[str] = kwargs.get('title')
        self.album: Optional[str] = kwargs.get('album')
        self.bitrate: Optional[int] = kwargs.get('bitrate')
        self.genre: Optional[str] = kwargs.get('genre')
        self.year: Optional[int] = kwargs.get('year')
        self.rating: Optional[int] = kwargs.get('rating')
        self.duration: Optional[int] = kwargs.get('duration')
        self.flac_filename: Optional[str] = kwargs.get('flac_filename')
        self.mp3_filename: Optional[str] = kwargs.get('mp3_filename')

    def has_metadata(self) -> bool:
        return any([x for x in self.__dict__.values()])

    def save_to_db(self) -> None:
        if not self.has_metadata():
            logging.warning(logging.warning(f"no metadata for {self.flac_filename}"))
        else:
            logging.info(f"inserting in db - {self.flac_filename}")
            conn = sqlite3.connect(env_settings.DATABASE_FILE)
            cursor = conn.cursor()

            insert_query = f'''
            INSERT INTO track ({','.join([k for k, v in self.__dict__.items() if v is not None])})
            VALUES ({','.join(['?' for k, v in self.__dict__.items() if v is not None])})
            '''
            values = tuple(v for k, v in self.__dict__.items() if v is not None)

            try:
                # Execute the insert command
                cursor.execute(insert_query, values)
                # Commit the changes
                conn.commit()
                logging.info(f"Track '{self.title}' by '{self.artist}' has been created successfully.")
            except sqlite3.IntegrityError as e:
                logging.info(f"Error: {self.flac_filename} already exists")
            finally:
                conn.close()

    @staticmethod
    def format_metadata(result: subprocess.CompletedProcess, flac_filename: str, mp3_filename: str) -> dict:
        metadata: Dict[str, Any] = {}
        raw_metadata = json.loads(result.stdout)

        if 'format' in raw_metadata and 'tags' in raw_metadata['format']:
            metadata.update({k.lower(): v for k, v in raw_metadata['format']['tags'].items()})
            metadata["flac_bit_rate"] = raw_metadata['format'].get('bit_rate', None)
            metadata["duration"] = raw_metadata['format'].get('duration', None)
            metadata["flac_filename"] = flac_filename
            metadata["mp3_filename"] = mp3_filename
            return metadata
        else:
            raise NoMetadataException

    def check_if_metadata_exists(self, flac_filename) -> bool:
        query = "SELECT artist FROM track WHERE flac_filename = ?"
        conn = sqlite3.connect(env_settings.DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute(query, (flac_filename,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()
        logging.info(result)
        return result is not None

    @staticmethod
    def get_metadata(flac_file, mp3_file) -> Dict[str, Any]:
        command = [env_settings.FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", flac_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            logging.error(f"Error running ffprobe: {result.stderr}")
            return {}

        return Track.format_metadata(result, flac_file, mp3_file)

    def from_flac(self, flac_file, mp3_file) -> 'Track':
        if self.check_if_metadata_exists(flac_file):
            logging.warning(f"exists in db {flac_file} skipping")
            raise ValueError
        try:
            metadata = self.get_metadata(flac_file, mp3_file)
        except NoMetadataException as e:
            logging.error(f"no metadata {e}")
            metadata = {}

        metadata_ci = CaseInsensitiveDict({k.lower(): v for k, v in metadata.items()})
        logging.debug(metadata_ci)

        return Track(
            artist=metadata_ci.get('artist'),
            title=metadata_ci.get('title'),
            album=metadata_ci.get('album'),
            bitrate=metadata_ci.get('flac_bit_rate'),
            genre=metadata_ci.get('genre'),
            year=metadata_ci.get('date'),
            duration=metadata_ci.get('duration'),
            flac_filename=metadata_ci.get('flac_filename'),
            mp3_filename=metadata_ci.get('mp3_filename')
        )
