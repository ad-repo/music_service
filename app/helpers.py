import os
import re
import subprocess


class CaseInsensitiveDict(dict):
    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def get(self, key, default=None):
        return super().get(key.lower(), default)


class NoMetadataException(Exception):
    pass


def get_multimedia_data(video_file: str) -> list:
    command = [
        os.environ.get("FFMPEG"), '-i', video_file
    ]
    # print(command)
    result = subprocess.run(command,
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            text=True)
    result_list = [line.strip() for line in result.stderr.split('\n')]
    return result_list


def match(line):
    pattern = 'Stream\s+#\d+:(\d+)\('
    match = re.search(pattern, line)
    if match:
        stream_num = match.group(1)
        # streams_numbers.append(stream_num)
        # print(stream_num, type(stream_num))
        return stream_num


def process_stream(line: str, remove_subtitles, english_subs_only):
    eng = '(eng)'
    if 'Subtitle' in line:
        if remove_subtitles:
            return None
        else:
            if eng in line:
                print(line)
                return match(line)
            else:
                if not english_subs_only:
                    print(line)
                    return match(line)

    if 'Audio' in line and eng in line:
        print(line)
        return match(line)


def build_map_args(stream_list: list):
    map_arg = '-map'
    map_args = []
    stream_list.append('0') if '0' not in stream_list else None
    for stream_num in stream_list:
        map_args.append(map_arg)
        map_args.append(f'0:{stream_num}')
    return map_args


def build_command(in_video_file: str, out_video_file, stream_list: list):
    command = [os.environ.get('FFMPEG'), '-i', in_video_file]
    command += build_map_args(stream_list)
    command += ['-y', '-c', 'copy', out_video_file]
    print(command)
    return command


def process_streams(video_data: list, remove_subtitles=True, english_subs_only=True) -> list:
    """
    get the stream numbers of the streams to keep, by default english and no subtitles
    :param video_data:
    :param remove_subtitles:
    :return:
    """
    print(video_data)
    streams_numbers = []
    for line in video_data:
        if 'Stream #' in line:
            stream_num = process_stream(line, remove_subtitles, english_subs_only)
            streams_numbers.append(stream_num) if stream_num is not None else None
    return streams_numbers
