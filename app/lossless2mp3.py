import logging
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from db import Track
from db import create_db

from settings import Settings
from constants import ROOT_DIR

env_settings = Settings()
for setting in env_settings:
    print(setting)



# Configure logging to capture both stdout and stderr
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='w'),
        logging.StreamHandler(sys.stdout),  # To log to stdout
        logging.StreamHandler(sys.stderr)   # To log to stderr
    ]
)

# Define a handler for uncaught exceptions
def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# Set the global exception handler to our handler
sys.excepthook = handle_uncaught_exception

def _convert(flac_path, mp3_path):
    command = [
        env_settings.FFMPEG, '-i', flac_path, '-ab', '320k', '-map_metadata', '0', '-id3v2_version', '3', mp3_path
    ]
    subprocess.run(command, check=True)


def convert(flac_path, mp3_path, dest_dir):
    if os.path.exists(mp3_path):
        logging.warning(f"skip mp3 conversion - mp3 exists: {mp3_path} for {flac_path}")
        return
    try:
        _convert(flac_path, mp3_path)
    except Exception as e:
        logging.error(f"ERROR {mp3_path}")
        with open(os.path.join(os.path.dirname(__file__), "mp3_convert_errors.txt"), "a+") as f:
            f.write(f"{mp3_path}\n")


def go(mp3_dir, flac_path, mp3_path, dest_dir):
    os.makedirs(mp3_dir, exist_ok=True)
    convert(flac_path, mp3_path, dest_dir)
    try:
        Track().from_flac(flac_path, mp3_path).save_to_db()
    except ValueError as e:
        return

def process_file(file: str, root: str, source_dir: str, dest_dir: str):
    if file.lower().endswith('.flac') or file.lower().endswith('.m4a'):
        logging.info(f"Converting {file}")
        flac_path = os.path.join(root, file)
        relative_path = os.path.relpath(root, source_dir)
        mp3_dir = os.path.join(dest_dir, relative_path)
        mp3_path = os.path.join(mp3_dir, os.path.splitext(file)[0] + '.mp3')
        go(mp3_dir, flac_path, mp3_path, dest_dir)  # Assuming 'go' handles conversion

# The walk function with multithreading
def walk(source_dir: str, dest_dir: str, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for root, dirs, files in os.walk(source_dir):
            # Submit tasks to the thread pool for each file
            for file in files:
                executor.submit(process_file, file, root, source_dir, dest_dir)


def convert_lossless_to_mp3(source_dir: str, dest_dir: str):
    logging.info(f"using db {env_settings.DATABASE_FILE}")
    create_db()
    logging.info(f"Converting flac to mp3 - SRC {source_dir} DEST {dest_dir}")
    walk(source_dir, dest_dir)


if __name__ == '__main__':
    if os.environ.get('LOCAL') == "true":
        convert_lossless_to_mp3(os.path.join(ROOT_DIR, "test_data"),
                                os.path.join(ROOT_DIR, "test_data_out"))
    else:
        convert_lossless_to_mp3(env_settings.FLAC_VOLUME, env_settings.MP3_VOLUME)

