import json
from typing import Optional, Dict, Any
from tinydb import TinyDB, Query
import subprocess
import os
from socket import gethostname

DEV_BOX = "ad-mbp.lan"
if gethostname() == DEV_BOX:
    FFPROBE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ffprobe")
else:
    FFPROBE = "ffprobe"

class CaseInsensitiveDict(dict):
    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def get(self, key, default=None):
        return super().get(key.lower(), default)

class Track:
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
        self.filename: Optional[str] = kwargs.get('filename')

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)

    def save_to_db(self, db: TinyDB) -> None:
        db.insert(self.__dict__)

    @staticmethod
    def from_json(json_str: str) -> 'Track':
        data: Dict[str, Any] = json.loads(json_str)
        return Track(**data)

    @staticmethod
    def from_db(record: Dict[str, Any]) -> 'Track':
        return Track(**record)

    @staticmethod
    def get_flac_metadata(file_path: str) -> Dict[str, Any]:
        print("FOO")
        command = [
            FFPROBE,
            "-v", "error",
            "-show_entries", "format_tags",
            "-of", "json",
            file_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"Error running ffprobe: {result.stderr}")
            return {}

        metadata = json.loads(result.stdout)

        print(f"Metadata: {metadata}")
        # Normalize keys to lowercase
        if 'format' in metadata and 'tags' in metadata['format']:
            metadata = {k.lower(): v for k, v in metadata['format']['tags'].items()}
        else:
            metadata = {}

        return metadata

    @staticmethod
    def from_flac(file_path: str) -> 'Track':
        metadata = Track.get_flac_metadata(file_path)
        print(metadata)
        metadata_ci = CaseInsensitiveDict({k.lower(): v for k, v in metadata.items()})

        return Track(
            artist=metadata_ci.get('artist'),
            title=metadata_ci.get('title'),
            album=metadata_ci.get('album'),
            bitrate=metadata_ci.get('bitrate'),
            genre=metadata_ci.get('genre'),
            year=metadata_ci.get('date'),  # or 'year' depending on your metadata
            duration=metadata_ci.get('duration'),  # might need to calculate duration separately
            filename=file_path
        )
