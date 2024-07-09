import json
import logging
import os
import subprocess
import sqlite3
from typing import Optional, Dict, Any

from helpers import CaseInsensitiveDict, NoMetadataException


# def db_factory():
#     if os.environ.get("DELETE_DATABASE_FILE") != "":
#         logging.warning(f"Deleting database file {'DATABASE_FILE'}")
#         try:
#             os.remove(os.environ.get('DATABASE_FILE'))
#         except FileNotFoundError:
#             logging.warning(f"delete failed did not find {os.environ.get('DATABASE_FILE')}")
#         os.environ.update({"DELETE_DATABASE_FILE": ""})
#     return TinyDB(os.environ.get('DATABASE_FILE'))

import sqlite3

def create_db():
    # Create a connection to the SQLite database (it will create the database if it does not exist)
    conn = sqlite3.connect(os.environ.get('DATABASE_FILE'))

    # Create a cursor object to interact with the database
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
        mp3_filename TEXT
    );
    '''

    logging.info(create_table_query)

    # Execute the create table command
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
            conn = sqlite3.connect('music_service.db')
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
                print(f"Track '{self.title}' by '{self.artist}' has been created successfully.")
            except sqlite3.IntegrityError as e:
                print(f"Error: {self.flac_filename} already exists")
            finally:
                # Close the connection
                conn.close()

    @staticmethod
    def format_metadata(result: subprocess.CompletedProcess, flac_filename: str, mp3_filename: str) -> dict:
        metadata: Dict[str, Any] = {}
        raw_metadata = json.loads(result.stdout)

        if 'format' in raw_metadata and 'tags' in raw_metadata['format']:
            metadata.update({k.lower(): v for k, v in raw_metadata['format']['tags'].items()})
            metadata["flac_bit_rate"] = raw_metadata['format']['bit_rate']
            metadata["duration"] = raw_metadata['format']['duration']
            metadata["flac_filename"] = flac_filename
            metadata["mp3_filename"] = mp3_filename
            return metadata
        else:
            raise NoMetadataException

    @staticmethod
    def get_metadata(flac_file, mp3_file) -> Dict[str, Any]:
        command = [os.environ.get("FFPROBE"), "-v", "quiet", "-print_format", "json", "-show_format", flac_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            logging.error(f"Error running ffprobe: {result.stderr}")
            return {}

        return Track.format_metadata(result, flac_file, mp3_file)

    def from_flac(self, flac_file, mp3_file) -> 'Track':
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
