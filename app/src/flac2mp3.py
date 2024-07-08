import logging
import os
import subprocess

from constants import DOCKER_MP3_VOLUME, DOCKER_FLAC_VOLUME, ROOT_DIR
from db import Track, db_factory

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("../app.log"),
    logging.StreamHandler()
])


def _convert(flac_path, mp3_path):
    command = [
        os.environ.get("FFMPEG"), '-i', flac_path, '-f', 'flac', '-b:a', '320k', '-map_metadata', '0', mp3_path
    ]
    subprocess.run(command, check=True)


def convert(flac_path, mp3_path, dest_dir):
    if os.path.exists(mp3_path):
        logging.warning(f"skip convert - mp3 exists: {mp3_path} for {flac_path}")
        return
    try:
        _convert(flac_path, mp3_path)
    except Exception as e:
        logging.error(f"ERROR {mp3_path}")
        with open(os.path.join(os.path.dirname(__file__), "mp3_convert_errors.txt"), "a+") as f:
            f.write(f"{mp3_path}\n")


def go(mp3_dir, flac_path, mp3_path, dest_dir, database):
    os.makedirs(mp3_dir, exist_ok=True)
    convert(flac_path, mp3_path, dest_dir)
    Track().from_flac(flac_path, mp3_path).save_to_db(database)


def convert_flac_to_mp3(source_dir: str, dest_dir: str):
    logging.info(f"using db {os.environ.get('DATABASE_FILE')}")
    database = db_factory()
    logging.info(f"Converting flac to mp3 - SRC {source_dir} DEST {dest_dir}")
    for root, dirs, files in os.walk(source_dir):
        print(root)
        continue
        for file in files:
            if file.lower().endswith('.flac'):
                logging.info(f"Converting {file}")
                flac_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, source_dir)
                mp3_dir = os.path.join(dest_dir, relative_path)
                mp3_path = os.path.join(mp3_dir, os.path.splitext(file)[0] + '.mp3')
                go(mp3_dir, flac_path, mp3_path, dest_dir, database)


if __name__ == '__main__':
    if os.environ.get('ENV') == "":
        # docker running on the nas with ffmpeg globally installed
        convert_flac_to_mp3(DOCKER_FLAC_VOLUME, DOCKER_MP3_VOLUME)
    else:
        # run for local development, no docker, no global ffmpeg installed
        convert_flac_to_mp3(os.path.join(ROOT_DIR, "test_data"),
                            os.path.join(ROOT_DIR, "test_data_out"))
