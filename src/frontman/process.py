from pathlib import Path
from typing import Iterable, Tuple, Union

from .schema import Manifest, PackageFile


def _get_src_and_dest(
    file: Union[str, PackageFile], destination: Path
) -> Tuple[str, Path]:
    if isinstance(file, str):
        file_source = file
        file_destination = destination / file
    else:
        file_source = file.name
        file_destination = destination / file.destination / file.name
        if file.rename is not None:
            file_destination = file_destination.parent / file.rename

    return file_source, file_destination


def generate_file_list(
    root_path: Path, manifest: Manifest
) -> Iterable[Tuple[str, Path]]:
    base_path = root_path / manifest.destination

    for package in manifest.packages:
        provider = package.provider or manifest.provider

        destination = base_path / (package.destination or "")
        name = package.name
        version = package.version

        for file in package.files:
            file_source, file_destination = _get_src_and_dest(file, destination)

            if package.path is not None:
                file_source = str(package.path / file_source)

            file_url = provider.get_file_url(name, version, file_source)

            yield (file_url, file_destination)
