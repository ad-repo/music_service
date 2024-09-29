import os
import subprocess
import constants
import shutil
import sys
import argparse

from helpers import get_multimedia_data, process_streams, build_command


def modify_track(video_file: str, outfile, stream_list: list):
    command = build_command(video_file, outfile, stream_list)
    print(f'--- >>> {command}')
    std_out, error_out = run_ffmpeg_command(command)
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

        # Print stdout and stderr
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
    os.chdir('/video')
    outfile = f'temp_{os.path.basename(video_file)}'
    data =  get_multimedia_data(video_file,)
    std_out, error_out = modify_track(video_file, outfile, process_streams(data, remove_subs, english_only_subs))
    swap(video_file, outfile)
    print(std_out)
    print(error_out)


if __name__ == "__main__":
    # remove_subs = sys.argv[1]
    # english_only_subs = sys.argv[2]
    # video_file = sys.argv[0]
    # # video_file = "/Users/ad/Projects/music_service/test_data/Monsters.The.Lyle.and.Erik.Menendez.Story.S01E02.1080p.NF.WEB-DL.H.264-EniaHD copy.mkv"
    # main(video_file, remove_subs, english_only_subs)
    parser = argparse.ArgumentParser(description="Process video metadata and optionally handle subtitles.")

    # Define expected arguments
    parser.add_argument('input_string', type=str, help="Input string for video metadata processing.")
    parser.add_argument('remove_subs', type=str, help="Remove subtitles (yes/no).")
    parser.add_argument('only_english_subs', type=str, help="Keep only English subtitles (yes/no).")

    # Parse the arguments
    args = parser.parse_args()

    # Convert the string 'yes'/'no' to boolean values
    remove_subs = args.remove_subs.lower() == 'yes'
    only_english_subs = args.only_english_subs.lower() == 'yes'

    # Call the processing function with the parsed arguments
    main(args.input_string, remove_subs, only_english_subs)
