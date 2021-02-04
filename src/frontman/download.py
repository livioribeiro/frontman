from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Iterable, Optional, Tuple

import requests

from .result import Result, Status


def ensure_destination(destination: Path):
    destination_dir = destination.parent
    if destination_dir.exists() and destination_dir.is_file():
        raise ValueError(f'"{destination}" is a file')

    if not destination_dir.exists():
        destination_dir.mkdir(mode=0o0755, parents=True, exist_ok=True)


def download_file(
    source: str, destination: Path, session: Optional[requests.Session] = None
):
    ensure_destination(destination)

    if session is not None:
        response = session.get(source)
    else:
        response = requests.get(source)
    response.raise_for_status()

    destination.write_bytes(response.content)


def download_concurrent(
    file_list: Iterable[Tuple[str, Path]],
    force: bool,
    concurrency: Optional[int] = None,
) -> Iterable[Result]:

    executor = ThreadPoolExecutor(max_workers=concurrency)
    session = requests.Session()

    def worker(item: Tuple[str, Path]):
        src, dest = item

        if dest.exists() and not force:
            return Result(Status.SKIP, src, dest)

        try:
            download_file(src, dest, session)
            result = Result(Status.OK, src, dest)
        except Exception as e:
            result = Result(Status.ERROR, src, None, e)

        return result

    for i in executor.map(worker, file_list):
        yield i

    # which one is faster, `executor.map` or `executor.submit`?
    #
    # future_list = [executor.submit(worker, i) for i in file_list]
    # for future in concurrent.futures.as_completed(future_list):
    #     yield future.result()

    executor.shutdown()
