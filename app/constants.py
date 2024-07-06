import os
from socket import gethostname

DEV_BOX = "ad-mbp.lan"
FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"
DB_FILENAME = "music_database.json"
DATABASE_FILE = f"/db/{DB_FILENAME}"
DEV_BOX_DATABASE_FILE = os.path.join(os.path.dirname(__file__), DB_FILENAME)
DEV_BOX_FFPROBE = os.path.join(os.path.dirname(os.path.dirname(__file__)), FFPROBE)
DEV_BOX_FFMPEG = os.path.join(os.path.dirname(os.path.dirname(__file__)), FFMPEG)
DELETE_DATABASE_FILE = ""
# DELETE_DATABASE_FILE = "True"

FILE_TYPES = ['flac']
DOCKER_FLAC_VOLUME = "/flac_dir"
DOCKER_MP3_VOLUME = "/mp3_dir"
DOCKER_SPLIT_VOLUME = "/split_dir"
APE_RENAME_STR = "ignore"
FLAC_RENAME_STR = "extracted"


if gethostname() == DEV_BOX:
    os.environ.update({"DELETE_DATABASE_FILE": DELETE_DATABASE_FILE})
    os.environ.update({"ENV": DEV_BOX})
    os.environ.update({"FFMPEG": DEV_BOX_FFMPEG})
    os.environ.update({"FFPROBE": DEV_BOX_FFPROBE})
    os.environ.update({"DATABASE_FILE": DEV_BOX_DATABASE_FILE})
else:
    os.environ.update({"DELETE_DATABASE_FILE": ""})
    os.environ.update({"ENV": ""})
    os.environ.update({"FFMPEG": FFMPEG})
    os.environ.update({"FFPROBE": FFPROBE})
    os.environ.update({"DATABASE_FILE": DATABASE_FILE})