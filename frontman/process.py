from pathlib import Path
import queue
import threading
from typing import Callable, Tuple, Iterable, Optional

from .schema import Manifest, PackageFile
from .provider import get_provider

import requests

MAX_THREAD = 4


def generate_file_list(root_path: Path, manifest: Manifest) -> Iterable[Tuple[str, Path]]:
    base_path = root_path / manifest.destination

    for package in manifest.packages:
        provider = get_provider(package.provider or manifest.provider)

        destination = base_path / (package.destination or '')
        name = package.name
        version = package.version

        for file in package.files:
            if isinstance(file, str):
                file_source = file
                file_destination = destination / file
            elif isinstance(file, PackageFile):
                file_source = file.name
                file_destination = destination / file.destination / file.name
                if file.rename is not None:
                    file_destination = file_destination.parent / file.rename
            else:
                raise TypeError('invalid package file type')

            if package.path is not None:
                file_source = str(package.path / file_source)

            file_url = provider.get_file_url(name, version, file_source)
            yield file_url, file_destination


def ensure_destination(destination: Path):
    destination_dir = destination.parent
    if destination_dir.exists() and destination_dir.is_file():
        raise ValueError(f'"{destination}" is a file')

    if not destination_dir.exists():
        destination_dir.mkdir(mode=0o0755, parents=True, exist_ok=True)


def download_file(source: str, destination: Path, session: Optional[requests.Session] = None):
    ensure_destination(destination)

    if session is not None:
        response = session.get(source)
    else:
        response = requests.get(source)
    response.raise_for_status()

    destination.write_bytes(response.content)


def download_concurrent(
        num_threads: int,
        file_list: Iterable[Tuple[str, Path]],
        success_callback: Callable[[str, Path], None],
        failure_callback: Callable[[str, Exception], None]):

    q = queue.Queue()
    list_len = 0
    for file in file_list:
        q.put(file)
        list_len += 1

    num_threads = min(num_threads, list_len)

    session = requests.Session()

    def worker():
        while True:
            src, dest = q.get()
            try:
                download_file(src, dest, session)
                success_callback(src, dest)
            except Exception as e:
                failure_callback(src, e)
            q.task_done()

    for i in range(num_threads):
        threading.Thread(target=worker, daemon=True).start()

    q.join()
