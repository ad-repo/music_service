import argparse
import os
import re
import shutil
import subprocess


from helpers import get_multimedia_data

from settings import Settings
from constants import ENGLISH

env_settings = Settings()
for setting in env_settings:
    print(setting)


def match(line: str) -> str or None:
    pattern = 'Stream\s+#\d+:(\d+)\('
    match = re.search(pattern, line)
    if match:
        stream_num = match.group(1)
        return stream_num


def process_stream(line: str, remove_subtitles: bool, english_subs_only: bool) -> str or None:
    if 'Subtitle' in line:
        if remove_subtitles:
            return None
        else:
            if ENGLISH in line:
                print(line)
                return match(line)
            else:
                if not english_subs_only:
                    print(line)
                    return match(line)

    if 'Audio' in line and ENGLISH in line:
        print(line)
        return match(line)


def process_streams(video_data: list, remove_subtitles=True, english_subs_only=True) -> list[str]:
    """
    get the stream numbers of the streams to keep, by default english and no subtitles:
    """
    print(video_data)
    streams_numbers = []
    for line in video_data:
        if 'Stream #' in line:
            stream_num = process_stream(line, remove_subtitles, english_subs_only)
            streams_numbers.append(stream_num) if stream_num is not None else None
    return streams_numbers


def build_map_args(stream_list: list) -> list[str]:
    map_arg = '-map'
    map_args = []
    stream_list.append('0') if '0' not in stream_list else None
    for stream_num in stream_list:
        map_args.append(map_arg)
        map_args.append(f'0:{stream_num}')
    return map_args


def build_command(in_video_file: str, out_video_file, stream_list: list) -> list[str]:
    command = [env_settings.FFMPEG, '-i', in_video_file]
    command += build_map_args(stream_list)
    command += ['-y', '-c', 'copy', out_video_file]
    return command


def modify_track(video_file: str, stream_list: list):
    outfile = f'temp_{os.path.basename(video_file)}'
    command = build_command(video_file, outfile, stream_list)
    print(f'--- >>> {command}')
    std_out, error_out = run_ffmpeg_command(command)
    swap(video_file, outfile)
    return std_out, error_out


def run_ffmpeg_command(command):
    try:
        result = subprocess.run(
            command,
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

        stdout_lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        stderr_lines = [line.strip() for line in result.stderr.split('\n') if line.strip()]

        print("Standard Output:")
        for line in stdout_lines:
            print(line)

        print("\nStandard Error:")
        for line in stderr_lines:
            print(line)

        return stdout_lines, stderr_lines

    except subprocess.CalledProcessError as e:
        print("An error occurred:")
        print("Return Code:", e.returncode)
        print("Output:", e.output)
        print("Error:", e.stderr)
        return None, None


def swap(in_video_file, out_video_file):
    os.remove(in_video_file)
    shutil.move(out_video_file, in_video_file)


def main(video_file, remove_subs, english_only_subs):
    # make VIDEO_DIR the working directory
    os.chdir(env_settings.VIDEO_DIR)
    data = get_multimedia_data(video_file)
    std_out, error_out = modify_track(video_file, process_streams(data, remove_subs, english_only_subs))


if __name__ == "__main__":
    if os.environ.get('LOCAL'):
        video_file = "/Users/ad/Projects/music_service/test_data/Monsters.The.Lyle.and.Erik.Menendez.Story.S01E02.1080p.NF.WEB-DL.H.264-EniaHD copy.mkv"
        main(video_file, True, True)
    else:
        parser = argparse.ArgumentParser(description="")
        parser.add_argument('video_filename', type=str, help="")
        parser.add_argument('remove_subs', type=str, help="", default='true')
        parser.add_argument('only_english_subs', type=str, help="", default='true')
        args = parser.parse_args()

        remove_subs = args.remove_subs.lower() == 'true'
        only_english_subs = args.only_english_subs.lower() == 'true'

        print(f"remove_subs: {remove_subs}")
        print(f"only_english_subs: {only_english_subs}")

        main(args.video_filename, remove_subs, only_english_subs)
