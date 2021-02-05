from pathlib import Path
from typing import Optional

import pytest
import requests

from frontman import download
from frontman.result import ErrorResult, SuccessResult


def test_ensure_destination_single_dir(tmp_path: Path):
    package_path = tmp_path / "package_path/package_file.js"
    assert not package_path.exists()
    assert not package_path.parent.exists()

    download.ensure_destination(package_path)
    assert not package_path.exists()
    assert package_path.parent.exists()


def test_ensure_destination_multiple_dir(tmp_path: Path):
    package_path = tmp_path / "package_path_1/package_path_2/package_file.js"
    assert not package_path.exists()
    assert not package_path.parent.exists()
    assert not package_path.parent.parent.exists()

    download.ensure_destination(package_path)
    assert not package_path.exists()
    assert package_path.parent.exists()
    assert package_path.parent.parent.exists()


def test_ensure_destination_dir_is_file_should_fail(tmp_path: Path):
    package_path = tmp_path / "package_path/package_file.js"
    package_path.parent.touch()
    assert package_path.parent.is_file()

    with pytest.raises(ValueError):
        download.ensure_destination(package_path)


def test_download_file_without_session(tmp_path: Path):
    package_file = "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.js"
    download_path = tmp_path / "jquery" / "jquery.js"

    download.download_file(package_file, download_path)

    assert download_path.exists()
    assert download_path.is_file()

    file_content = download_path.read_text()
    assert "jQuery JavaScript Library v3.5.1" in file_content


def test_download_file_with_session(tmp_path: Path):
    package_file = "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.js"
    download_path = tmp_path / "jquery" / "jquery.js"

    session = requests.session()
    download.download_file(package_file, download_path, session)

    assert download_path.exists()
    assert download_path.is_file()

    file_content = download_path.read_text()
    assert "jQuery JavaScript Library v3.5.1" in file_content


def _download_concurrent(tmp_path: Path, concurrency: Optional[int]):
    file_list = [
        "https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.min.js",
        "https://unpkg.com/@popperjs/core@2.6.0/dist/umd/popper.min.js",
        "https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.min.js",
        "https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css",
    ]
    path_list = [
        tmp_path / "jquery" / "jquery.min.js",
        tmp_path / "popper" / "popper.min.js",
        tmp_path / "bootstrap" / "js" / "bootstrap.min.js",
        tmp_path / "bootstrap" / "css" / "bootstrap.min.css",
    ]

    for p in path_list:
        assert not p.exists()

    results = list(
        download.download_concurrent(zip(file_list, path_list), concurrency=concurrency)
    )

    for p, r in zip(path_list, results):
        assert isinstance(r, SuccessResult)
        assert p.exists()
        assert p == r.destination


def test_download_concurrent_with_concurrency_set(tmp_path: Path):
    _download_concurrent(tmp_path, 4)


def test_download_concurrent_without_concurrency_set(tmp_path: Path):
    _download_concurrent(tmp_path, None)


def test_download_concurrent_skip(tmp_path: Path):
    file_list = [
        (
            "https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.min.js",
            tmp_path / "jquery" / "jquery.min.js",
        )
    ]

    result_new = next(iter(download.download_concurrent(file_list)))
    assert isinstance(result_new, SuccessResult)
    assert not result_new.skip

    result_skip = next(iter(download.download_concurrent(file_list)))
    assert isinstance(result_skip, SuccessResult)
    assert result_skip.skip


def test_download_concurrent_error(tmp_path: Path):
    file_list = [
        (
            "https://cdn.jsdelivr.net/npm/this/does/not/exist",
            tmp_path / "does" / "not" / "exist",
        )
    ]

    result = next(iter(download.download_concurrent(file_list)))
    assert isinstance(result, ErrorResult)
