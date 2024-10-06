import os
from socket import gethostname
from dotenv import load_dotenv

load_dotenv()

ME = gethostname()

def get_dev_box(dev_boxes):
    for name in dev_boxes:
        if ME == name:
            return name

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
# DEV_BOXES = "ad-mbp.lan", "ad-mbp.local"
DEV_BOX = get_dev_box(os.getenv('DEV_BOXES').split(','))
# FFMPEG = "ffmpeg"
# FFPROBE = "ffprobe"
# DB_FILENAME = "music_database.db"
DATABASE_FILE = f"/db/{os.getenv('DB_FILENAME')}"
DEV_BOX_DATABASE_FILE = os.path.join(ROOT_DIR, "app", os.getenv('DB_FILENAME'))
DEV_BOX_FFPROBE = os.path.join(ROOT_DIR, "app", os.getenv('FFPROBE'))
DEV_BOX_FFMPEG = os.path.join(ROOT_DIR, "app", os.getenv('FFMPEG'))
DEV_BOX_SPLIT_DIR = "split_dir"
DEV_BOX_VIDEO_DIR = "/Users/ad/Projects/music_service/test_data"

# <<<<<<< HEAD
# SPLIT_FILE_TYPES = ['flac', 'ape', 'wv']
# DOCKER_FLAC_VOLUME = "/flac_dir"
# DOCKER_MP3_VOLUME = "/mp3_dir"
# DOCKER_SPLIT_VOLUME = "/split_dir"
# FLAC_RENAME_STR = "extracted"
# =======
# # os.environ.update({"ROOT_DIR": ROOT_DIR})
# >>>>>>> 256a2cf (refactor)
VIDEO_DIR = "/video"
ENGLISH = '(eng)'


# my local development with no docker and no ffmpeg/ffprobe in PATH
if ME == DEV_BOX:
    os.environ.update({"DELETE_DATABASE_FILE": ""})
    os.environ.update({"ENV": DEV_BOX})
    os.environ.update({"FFMPEG": DEV_BOX_FFMPEG})
    os.environ.update({"FFPROBE": DEV_BOX_FFPROBE})
    os.environ.update({"DATABASE_FILE": DEV_BOX_DATABASE_FILE})
    os.environ.update({"VIDEO_DIR": DEV_BOX_VIDEO_DIR})
    # os.environ.update({"SPLIT_DIR": DEV_BOX_SPLIT_DIR})
    SPLIT_DIR = DEV_BOX_SPLIT_DIR
else:
    # deployed on docker in synology nas
    os.environ.update({"DELETE_DATABASE_FILE": ""})
    os.environ.update({"ENV": ""})
    # os.environ.update({"FFMPEG": os.getenv('FFMPEG')})
    # os.environ.update({"FFPROBE": os.getenv('FFPROBE')})
    os.environ.update({"DATABASE_FILE": DATABASE_FILE})
    os.environ.update({"VIDEO_DIR": VIDEO_DIR})
    # os.environ.update({"SPLIT_DIR": DOCKER_SPLIT_VOLUME})
    SPLIT_DIR = os.getenv('DOCKER_SPLIT_VOLUME')