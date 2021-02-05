from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Iterable, Optional, Tuple, Union

import requests

from .result import ErrorResult, SuccessResult


def ensure_destination(destination: Path):
    destination_dir = destination.parent
    if destination_dir.exists() and destination_dir.is_file():
        raise ValueError(f"'{destination}' is a file")

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
    force: bool = False,
    concurrency: Optional[int] = None,
) -> Iterable[Union[SuccessResult, ErrorResult]]:

    executor = ThreadPoolExecutor(max_workers=concurrency)
    session = requests.Session()

    def worker(item: Tuple[str, Path]):
        src, dest = item

        if dest.exists() and not force:
            return SuccessResult(src, dest, skip=True)

        try:
            download_file(src, dest, session)
            return SuccessResult(src, dest)
        except Exception as e:
            return ErrorResult(src, e)

    for i in executor.map(worker, file_list):
        yield i

    # which one is faster, `executor.map` or `executor.submit`?
    #
    # future_list = [executor.submit(worker, i) for i in file_list]
    # for future in concurrent.futures.as_completed(future_list):
    #     yield future.result()

    executor.shutdown()
