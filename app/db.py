import json
import logging
import os
import subprocess
from typing import Optional, Dict, Any

from tinydb import TinyDB, Query

from helpers import CaseInsensitiveDict, NoMetadataException


def db_factory():
    if os.environ.get("DELETE_DATABASE_FILE") != "":
        logging.warning(f"Deleting database file {'DATABASE_FILE'}")
        try:
            os.remove(os.environ.get('DATABASE_FILE'))
        except FileNotFoundError:
            logging.warning(f"delete failed did not find {os.environ.get('DATABASE_FILE')}")
        os.environ.update({"DELETE_DATABASE_FILE": ""})
    return TinyDB(os.environ.get('DATABASE_FILE'))


class Track:
    """
    Track class is a music track with 2 possible versions flac with and mp3
    """

    def __init__(self, **kwargs: Optional[Dict[str, Any]]):
        self.artist: Optional[str] = kwargs.get('artist')
        self.title: Optional[str] = kwargs.get('title')
        self.album: Optional[str] = kwargs.get('album')
        self.encoding: Optional[str] = kwargs.get('encoding')
        self.bitrate: Optional[int] = kwargs.get('bitrate')
        self.genre: Optional[str] = kwargs.get('genre')
        self.year: Optional[int] = kwargs.get('year')
        self.rating: Optional[int] = kwargs.get('rating')
        self.duration: Optional[int] = kwargs.get('duration')
        self.flac_filename: Optional[str] = kwargs.get('flac_filename')
        self.mp3_filename: Optional[str] = kwargs.get('mp3_filename')

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)

    def has_metadata(self) -> bool:
        return any([x for x in self.__dict__.values()])

    def track_exists(self, db) -> str:
        query = Query()
        return db.search((query.flac_filename == self.flac_filename))

    def save_to_db(self, db: TinyDB, commpleted_tracks: list) -> None:
        if not self.has_metadata():
            logging.warning(logging.warning(f"no metadata for {self.flac_filename}"))
        # elif self.track_exists(db):
        elif self.flac_filename in commpleted_tracks:
            logging.warning(f"db record exists {self.flac_filename}")
        else:
            logging.info(f"inserting in db - {self.flac_filename}")
            db.insert(self.__dict__)
            commpleted_tracks.append(self.flac_filename)

    @staticmethod
    def from_json(json_str: str) -> 'Track':
        data: Dict[str, Any] = json.loads(json_str)
        return Track(**data)

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
