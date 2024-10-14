import logging
import os
import shutil
import subprocess
import sys
import uuid
import argparse
from datetime import datetime

from settings import Settings
from constants import SPLIT_FILE_TYPES, FLAC_RENAME_STR

env_settings = Settings()
for setting in env_settings:
    print(setting)

# exit()
#
# print(f"Database Filename: {settings.DATABASE_FILE}")

import chardet

# from constants import ROOT_DIR

# Configure logging to capture both stdout and stderr
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='w'),
        logging.StreamHandler(sys.stdout),  # To log to stdout
        logging.StreamHandler(sys.stderr)  # To log to stderr
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


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    confidence = result['confidence']
    return encoding if confidence > 0.8 else None


def get_track_length_1(duration_line):
    """
    duration_line could be in several formats
    ['  Duration: 00:57:42.61, start: 0.000000, bitrate: 999 kb/s']
    :param duration_line:
    :return:
    """
    d = duration_line[0].split(',')[0].split()[1]
    parts = d.split(':')
    return extract_times(parts)


def get_track_length_2(duration_line):
    """
    duration_line could be in several formats
    :param duration_line:
    :return:
    """
    d = [x for x in duration_line if "Duration:" in x]
    d1 = d[0].split(",")[0].split("Duration: ")[1]
    parts = d1.split(':')
    return extract_times(parts)


def extract_times(parts):
    h = int(parts[0])
    min = int(parts[1]) + (h * 60)
    sec = int(parts[2].split('.')[0])  # Extract seconds and remove milliseconds
    ms = int(parts[2].split('.')[1])  # Extract milliseconds
    formatted_duration = f"{min}:{sec}:{ms}".encode('utf-8')
    logging.debug(f"Formatted duration: {formatted_duration}")
    return formatted_duration


def get_track_length(file_path):
    formatted_duration = None
    result = subprocess.run(
        [env_settings.FFMPEG, '-i', file_path],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    duration_line = [line for line in result.stderr.split('\n') if "Duration" in line]
    logging.debug(f'Duration line: {duration_line}')
    if duration_line:
        try:
            print("1")
            return get_track_length_1(duration_line)
        except Exception as e:
            print("2")
            return get_track_length_2(duration_line)
    return None


def time_dif(time1, time2):
    # Convert byte strings to regular strings
    time1_str = time1.decode('utf-8')
    time2_str = time2.decode('utf-8')

    # Define the format
    time_format = '%H:%M:%S'

    # Parse the times into datetime objects
    time1_dt = datetime.strptime(time1_str, time_format)
    time2_dt = datetime.strptime(time2_str, time_format)

    # Calculate the difference
    time_difference = time2_dt - time1_dt

    # Get the difference in seconds
    time_difference_seconds = time_difference.total_seconds()
    logging.debug(f'Time difference (seconds): {time_difference_seconds}')
    return time_difference_seconds


def timedif(i1, i2):
    i1, i2 = i1.split(":"), i2.split(":")
    a = (int(i1[0]) * 60) + int(i1[1])
    b = (int(i2[0]) * 60) + int(i2[1])
    return b - a


def fix_cue_file(cuefile):
    """
    remove extra INDEX lines from cuefile
    :param cuefile:
    :return:
    """

    with open(cuefile, 'r+', encoding='utf-8', newline='', errors='ignore') as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        logging.debug(f'Processing line: {line.strip()}')
        if "INDEX 00" in line.strip():
            continue
        else:
            new_lines.append(line)
    with open(cuefile, 'w') as f:
        f.writelines(new_lines)
    print("leaving fix_cue_file")


def cuedata(pth):
    metadata = {b"TITLE": [], b"PERFORMER": [], b"INDEX": [], b"REM COMPOSER": []}
    logging.debug(f'Cue data path: {pth}')
    with open(pth, "+r", encoding="utf-8") as ff:
        f = ff.read()
        k = f.encode('utf-8')
    ff = k.split(b"TRACK")
    ff.pop(0)
    print("ff", ff)
    for i in ff:
        logging.debug(f'i: {i}')
        for spi in i.split(b"\n"):
            for ky in metadata:
                if ky in spi:
                    if ky == b"INDEX":
                        spi = spi.split(ky)[1].strip().split(b" ")[1]
                    else:
                        spi = spi.split(ky)[1].strip().strip(b'""')
                    metadata[ky].append(spi)
                    break
    return metadata


def chaff(time):
    min, sec = time.split(':')
    min = int(min)
    sec = int(sec)
    if min > 59:
        hr = min // 60
        min %= 60
        if hr == 0:
            return "%02d:%02d" % (min, sec)
        elif hr < 10:
            return "0%0d:%02d:%02d" % (hr, min, sec)
        else:
            return "%d:%02d:%02d" % (hr, min, sec)
    return time


def fix_title(name):
    for bad_char in ['/', '\\', '?', '%', '*', ':', '|', '”', '<', '>']:
        if bad_char in name:
            name = name.replace(bad_char, '')
    return name


def rename_flac(flac_file, base_dir):
    try:
        shutil.move(flac_file, os.path.join(base_dir, f"{os.path.basename(flac_file)}.{FLAC_RENAME_STR}"))
        print(f"{os.path.join(base_dir, os.path.basename(flac_file))}.{FLAC_RENAME_STR}")
    except Exception:
        shutil.move(flac_file,
                    os.path.join(base_dir, f"{os.path.basename(flac_file)}.{FLAC_RENAME_STR}_{uuid.uuid4()}"))
        print(os.path.join(base_dir, f"{os.path.basename(flac_file)}.{FLAC_RENAME_STR}_{uuid.uuid4()}"))


def cleanup(flac_file, base_dir):
    print(flac_file, base_dir)
    # rename_flac(flac_file, base_dir)


def get_track_times(cue_data, flac_file, pos):
    track_start_end_times = cue_data[b'INDEX'][pos:pos + 2]

    if len(track_start_end_times) == 1:
        logging.warning("going to try to get track length")
        track_start_end_times.append(get_track_length(flac_file))

    logging.debug(f'Track start and end times: {track_start_end_times}')
    stime, etime = track_start_end_times[0].decode('utf-8').strip(), track_start_end_times[1].decode(
        'utf-8').strip()
    return stime, etime


def get_map(audio_track_only):
    if audio_track_only:
        return "0:a"
    return "0"


"""
1. add analysis of streams in the file using 
    ffprobe -v error -show_streams inputfile or 
    ffprobe -v error -show_entries stream=index,codec_type -of default=noprint_wrappers=1 input.ape
"""


def create_track(flac_file, stime, diff, title, artist, pos, flac_outfile, audio_track_only):

    if flac_file.endswith('.flac'):
        cmd = [env_settings.FFMPEG,
               "-hide_banner",
               "-ss", stime,
               "-y",
               "-i", flac_file,
               "-t", diff,
               "-map", get_map(audio_track_only),
               "-max_muxing_queue_size", "9999",
               "-metadata", title,
               "-metadata", artist,
               "-metadata",
               f'track={pos}',
               flac_outfile]

    elif flac_file.endswith('.ape'):
        cmd = [env_settings.FFMPEG,
               "-hide_banner",
               "-ss", stime,
               "-y",
               "-i", flac_file,
               "-t", diff,
               "-map", get_map(audio_track_only),
               "-max_muxing_queue_size", "9999",
               "-c", "flac",
               "-metadata", title,
               "-metadata", artist,
               "-metadata", f'track={pos}',
               flac_outfile]

    elif flac_file.endswith('.wv'):
        cmd = [env_settings.FFMPEG,
               "-hide_banner",
               "-ss", stime,
               "-y",
               "-i", flac_file,
               "-t", diff,
               "-map", get_map(audio_track_only),
               "-max_muxing_queue_size", "9999",
               "-c", "flac",
               "-metadata", title,
               "-metadata", artist,
               "-metadata", f'track={pos}',
               flac_outfile]
    else:
        cmd = [env_settings.FFMPEG,
               "-hide_banner",
               "-ss", stime,
               "-y",
               "-i", flac_file,
               "-t", diff,
               "-map", get_map(audio_track_only),
               "-max_muxing_queue_size", "9999",
               "-c", "flac",
               "-metadata", title,
               "-metadata", artist,
               "-metadata", f'track={pos}',
               flac_outfile]

    # print(cmd)
    # print(os.path.abspath(os.curdir));exit()

    job = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    logging.debug(f'FFmpeg job output: {job}')

    if job.returncode > 0:
        raise Exception(f'FFmpeg failed for {title}')

    return job


def run_service(cue_file, music_file, music_outdir_fpath, base_dir, ext, sim_mode):
    cue_data = cuedata(cue_file)
    print("-", music_file)
    for pos, title in enumerate(cue_data[b'TITLE']):
        logging.info(f'Processing track: {title}')
        title = title.decode('utf-8')
        outfile = os.path.join(music_outdir_fpath, f'{fix_title(title)}.flac')
        title = f'title={title}'
        try:
            artist = 'artist=' + cue_data[b'PERFORMER'][pos].decode('utf-8')
        except Exception:
            artist = 'artist=' + os.path.splitext(os.path.basename(music_file))[0]
        stime, etime = get_track_times(cue_data, music_file, pos)
        diff = str(timedif(stime, etime))
        stime = chaff(stime.rsplit(":", 1)[0])
        if not sim_mode:
            try:
                job = create_track(music_file, stime, diff, title, artist, pos, outfile, False)
            except Exception as e1:
                logging.error(f"Initial attempt failed: {e1}. Retrying with audio_track_only=True.")
                try:
                    job = create_track(music_file, stime, diff, title, artist, pos, outfile, True)
                except Exception as e2:
                    logging.error(f"Retry failed: {e2}.")
                    job = None  # or some other fallback mechanism
            finally:
                logging.debug("Track creation process completed.")

    if not sim_mode:
        cleanup(music_file, base_dir)


def find_music_file(cue_file, music_indir_fpath):
    for file_ext in SPLIT_FILE_TYPES:
        root, ext = os.path.splitext(cue_file)

        if root.endswith(file_ext):
            music_file = root
        else:
            music_file = f"{root}.{file_ext}"

        music_file = os.path.join(music_indir_fpath, music_file)
        logging.debug(f'-- {music_file}')
        if os.path.exists(music_file):
            music_file.replace("'", "")
            music_file.replace("'", "")
            return music_file, file_ext
    return None, None


# def parse_folder(music_indir_fpath, music_outdir_fpath):
def parse_folder(cue_file, base_dir, sim_mode):
    cue_dir = os.path.dirname(cue_file)
    if cue_file is None:
        logging.warning(f"No cue file found in {cue_dir}")
        return -1

    music_file, file_ext = find_music_file(cue_file, cue_dir)
    logging.debug(music_file)

    try:
        fix_cue_file(cue_file)
    except ValueError:
        return -1

    if music_file is None:
        logging.warning(f"No flac file found for cue {cue_file}")
        return -1

    run_service(cue_file, music_file, cue_dir, base_dir, file_ext, sim_mode)


def find_music_folders(base_dir, sim_mode=False):
    print(base_dir)
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".cue"):
                logging.info(f"Found cue file: {file}, {root}")
                parse_folder(os.path.join(root, file), base_dir, sim_mode)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Optional cue_dir argument example")
    parser.add_argument('--cue_dir', type=str, help="Optional cue directory", default=None)
    args = parser.parse_args()

    if args.cue_dir is None:
        find_music_folders(env_settings.SPLIT_VOLUME)
    else:
        plex_lib_dir_name = 'AD-FLAC'
        docker_lib_name = 'flac_dir'

        cue_dir = args.cue_dir.replace(plex_lib_dir_name, docker_lib_name) if plex_lib_dir_name in args.cue_dir \
            else args.cue_dir

        print(f'Found cue dir: {args.cue_dir} : {cue_dir}')
        print(args.cue_dir, os.path.exists(cue_dir))

        # set new not defualt base dir to search
        SPLIT_DIR = cue_dir

        find_music_folders(args.cue_dir)
