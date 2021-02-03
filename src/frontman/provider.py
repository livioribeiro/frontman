from enum import Enum

_TEMPLATES = {
    "CDNJS": "https://cdnjs.cloudflare.com/ajax/libs/{package}/{version}/{file}",
    "JSDELIVR": "https://cdn.jsdelivr.net/npm/{package}@{version}/{file}",
    "UNPKG": "https://unpkg.com/{package}@{version}/{file}",
}


class Provider(str, Enum):
    CDNJS = "cdnjs"
    JSDELIVR = "jsdelivr"
    UNPKG = "unpkg"

    def get_file_url(self, package: str, version: str, file: str) -> str:
        if self.name not in _TEMPLATES:
            raise TypeError("unknown provider")

        return _TEMPLATES[self.name].format(package=package, version=version, file=file)
