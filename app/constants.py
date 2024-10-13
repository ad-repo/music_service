import os
from socket import gethostname
import yaml


def get_local_name(local_names):
    for name in local_names:
        if gethostname() == name:
            return True

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

    # network names for my development local server
    # IS_LOCAL_NAME = get_local_name(os.getenv('LOCAL_NAMES').split(','))
# FFMPEG = "ffmpeg"
# FFPROBE = "ffprobe"
# DB_FILENAME = "music_database.db"
# DATABASE_FILE = f"/db/{os.getenv('DB_FILENAME')}"
# DEV_BOX_DATABASE_FILE = os.path.join(ROOT_DIR, "app", os.getenv('DB_FILENAME'))
# DEV_BOX_FFPROBE = os.path.join(ROOT_DIR, "app", os.getenv('FFPROBE'))
# DEV_BOX_FFMPEG = os.path.join(ROOT_DIR, "app", os.getenv('FFMPEG'))
# DEV_BOX_SPLIT_DIR = "split_dir"
# DEV_BOX_VIDEO_DIR = "/Users/ad/Projects/music_service/test_data"
#
# # <<<<<<< HEAD
SPLIT_FILE_TYPES = ['flac', 'ape', 'wv']
FLAC_RENAME_STR = 'extracted'
ENGLISH = '(eng)'
# # DOCKER_FLAC_VOLUME = "/flac_dir"
# # DOCKER_MP3_VOLUME = "/mp3_dir"
# # DOCKER_SPLIT_VOLUME = "/split_dir"
# # FLAC_RENAME_STR = "extracted"
# # =======
# # # os.environ.update({"ROOT_DIR": ROOT_DIR})
# # >>>>>>> 256a2cf (refactor)
# VIDEO_DIR = "/video"
# ENGLISH = '(eng)'

local_flag = False
f = None

# my local development with no docker and no ffmpeg/ffprobe in PATH
if os.path.exists(os.path.join(ROOT_DIR, '.env-local.yml')):
    f = 'env-local.yaml'
    with open(f, "r") as file:
        local_config = yaml.safe_load(file)
    if get_local_name(local_config.LOCAL_NAMES.split(',')):
        local_flag = True

if not local_flag:
    f = '.env-synology-docker.yaml'

with open(f, "r") as file:
    config = yaml.safe_load(file)
os.environ.update({"DB_FILENAME": "DB_FILENAME"})
os.environ.update({"ENV": gethostname()})
os.environ.update({"FFMPEG": config.get("FFMPEG")})
os.environ.update({"FFPROBE": config.get("FFPROBE")})
os.environ.update({"DATABASE_FILE": config.get("DATABASE_FILE")})
os.environ.update({"VIDEO_DIR": config.get("VIDEO_DIR")})
os.environ.update({"SPLIT_DIR": config.get("CUE_SPLIT_OUT_DIR")})
