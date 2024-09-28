import os
import subprocess
import constants
import shutil

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
    outfile = os.path.join(os.path.dirname(video_file), f'temp_{os.path.basename(video_file)}')
    data =  get_multimedia_data(video_file,)
    std_out, error_out = modify_track(video_file, outfile, process_streams(data, remove_subs, english_only_subs))
    swap(video_file, outfile)
    print(std_out)
    print(error_out)


if __name__ == "__main__":
    remove_subs = True
    english_only_subs = True
    video_file = "/Users/ad/Projects/music_service/test_data/Monsters.The.Lyle.and.Erik.Menendez.Story.S01E02.1080p.NF.WEB-DL.H.264-EniaHD copy.mkv"
    main(video_file, remove_subs, english_only_subs)
