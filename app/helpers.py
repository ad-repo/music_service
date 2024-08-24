class CaseInsensitiveDict(dict):
    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def get(self, key, default=None):
        return super().get(key.lower(), default)

class NoMetadataException(Exception):
    pass