import subprocess
import os

from settings import Settings

env_settings = Settings()
for setting in env_settings:
    print(setting)

class CaseInsensitiveDict(dict):
    def __getitem__(self, key) -> str:
        return super().__getitem__(key.lower())

    def get(self, key, default=None) -> dict:
        return super().get(key.lower(), default)


class NoMetadataException(Exception):
    pass


def get_multimedia_data(video_file: str) -> list[str]:
    print(os.path.abspath(os.getcwd()))
    command = [
        env_settings.FFMPEG, '-i', video_file
    ]
    result = subprocess.run(command,
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            text=True)
    result_list = [line.strip() for line in result.stderr.split('\n')]
    return result_list



