import os
from socket import gethostname

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEV_BOX = "ad-mbp.lan"
FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"
DB_FILENAME = "music_database.json"
DATABASE_FILE = f"/db/{DB_FILENAME}"
DEV_BOX_DATABASE_FILE = os.path.join(ROOT_DIR, "app", DB_FILENAME)
DEV_BOX_FFPROBE = os.path.join(ROOT_DIR, "app", FFPROBE)
DEV_BOX_FFMPEG = os.path.join(ROOT_DIR, "app", FFMPEG)

FILE_TYPES = ['flac']
DOCKER_FLAC_VOLUME = "/flac_dir"
DOCKER_MP3_VOLUME = "/mp3_dir"
DOCKER_SPLIT_VOLUME = "/split_dir"
APE_RENAME_STR = "ignore"
FLAC_RENAME_STR = "extracted"

# local development no docker
if gethostname() == DEV_BOX:
    os.environ.update({"DELETE_DATABASE_FILE": "True"})
    os.environ.update({"ENV": DEV_BOX})
    os.environ.update({"FFMPEG": DEV_BOX_FFMPEG})
    os.environ.update({"FFPROBE": DEV_BOX_FFPROBE})
    os.environ.update({"DATABASE_FILE": DEV_BOX_DATABASE_FILE})
else:
    # deployed on docker in nas/prod
    os.environ.update({"DELETE_DATABASE_FILE": ""})
    os.environ.update({"ENV": ""})
    os.environ.update({"FFMPEG": FFMPEG})
    os.environ.update({"FFPROBE": FFPROBE})
    os.environ.update({"DATABASE_FILE": DATABASE_FILE})