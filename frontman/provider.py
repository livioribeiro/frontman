from enum import Enum

_CDNJS_TEMPLATE = 'https://cdnjs.cloudflare.com/ajax/libs/{package}/{version}/{file}'
_UNPKG_TEMPLATE = 'https://unpkg.com/{package}@{version}/{file}'
_JSDELIVR_TEMPLATE = 'https://cdn.jsdelivr.net/npm/{package}@{version}/{file}'


class ProviderEnum(str, Enum):
    CDNJS = 'cdnjs'
    JSDELIVR = 'jsdelivr'
    UNPKG = 'unpkg'


class Provider:
    def __init__(self, download_file_template):
        self.download_file_template = download_file_template

    def get_file_url(self, package: str, version: str, file: str) -> str:
        return self.download_file_template.format(package=package, version=version, file=file)


_CDNJS_PROVIDER = Provider(_CDNJS_TEMPLATE)
_UNPKG_PROVIDER = Provider(_UNPKG_TEMPLATE)
_JSDELIVR_PROVIDER = Provider(_JSDELIVR_TEMPLATE)


def get_provider(provider: ProviderEnum) -> Provider:
    if provider == ProviderEnum.CDNJS:
        return _CDNJS_PROVIDER
    if provider == ProviderEnum.UNPKG:
        return _UNPKG_PROVIDER
    if provider == ProviderEnum.JSDELIVR:
        return _JSDELIVR_PROVIDER

    raise ValueError('unknown provider')


