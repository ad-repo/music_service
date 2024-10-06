import subprocess
import os


class CaseInsensitiveDict(dict):
    def __getitem__(self, key) -> str:
        return super().__getitem__(key.lower())

    def get(self, key, default=None) -> dict:
        return super().get(key.lower(), default)


class NoMetadataException(Exception):
    pass


def get_multimedia_data(video_file: str) -> list[str]:
    command = [
        os.environ.get("FFMPEG"), '-i', video_file
    ]
    result = subprocess.run(command,
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            text=True)
    result_list = [line.strip() for line in result.stderr.split('\n')]
    return result_list



