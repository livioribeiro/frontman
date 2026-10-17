import os
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests
from typer.testing import CliRunner

from frontman.main import app

runner = CliRunner()


MANIFEST_OK = Path(__file__).parent / "frontman.json"
MANIFEST_WRONG_FILE_TYPE = Path(__file__).parent / "manifest.pdf"
MANIFEST_INVALID_JSON = Path(__file__).parent / "invalid.json"
MANIFEST_INVALID_SCHEMA = Path(__file__).parent / "invalid-schema.json"
MANIFEST_INVALID_PACKAGE = Path(__file__).parent / "invalid-package.json"
MANIFEST_DOES_NOT_EXIST = Path(__file__).parent / "does-not-exist.json"
MANIFEST_IS_DIR = Path(__file__).parent


def test_app_ok(tmp_path: Path):
    cwd = Path.cwd()
    os.chdir(tmp_path)

    result = runner.invoke(app, f"install {MANIFEST_OK} -w {tmp_path}")

    os.chdir(cwd)

    assert result.exit_code == 0
    assert (tmp_path / "assets").exists()
    assert (tmp_path / "assets").is_dir()
    assert (tmp_path / "assets" / "jquery" / "jquery.min.js").is_file()


def test_workdir_ok(tmp_path: Path):

    result = runner.invoke(app, f"install {MANIFEST_OK} -w {tmp_path}")

    assert result.exit_code == 0
    assert (tmp_path / "assets").exists()
    assert (tmp_path / "assets").is_dir()
    assert (tmp_path / "assets" / "jquery" / "jquery.min.js").is_file()


def test_invalid_manifest_file_type_should_fail():
    result = runner.invoke(app, f"install {MANIFEST_WRONG_FILE_TYPE}")

    assert result.exit_code != 0
    assert "Manifest must be in JSON format." in result.stdout


def test_invalid_manifest_format_should_fail():
    result = runner.invoke(app, f"install {MANIFEST_INVALID_JSON}")

    assert result.exit_code != 0
    assert "Manifest contains invalid JSON" in result.stdout


def test_invalid_manifest_schema_should_fail():
    result = runner.invoke(app, f"install {MANIFEST_INVALID_SCHEMA}")

    assert result.exit_code != 0
    assert "Manifest is not in expected format" in result.stdout


def test_non_existent_manifest_should_fail():
    result = runner.invoke(app, f"install {MANIFEST_DOES_NOT_EXIST}")

    assert result.exit_code != 0
    assert f"Manifest file '{MANIFEST_DOES_NOT_EXIST}' does not exist." in result.stdout


def test_manifest_as_dir_should_fail():
    result = runner.invoke(app, f"install {MANIFEST_IS_DIR}")

    assert result.exit_code != 0
    assert f"Given manifest '{MANIFEST_IS_DIR}' must be a file." in result.stdout


def test_non_positive_concurrency_value_should_fail():
    result = runner.invoke(app, f"install {MANIFEST_OK} -c 0")

    assert result.exit_code != 0
    assert "Value must be greater than 0." in result.stdout


def test_negative_concurrency_value_should_fail():
    result = runner.invoke(app, f"install {MANIFEST_OK} -c -1")

    assert result.exit_code != 0
    assert "Value must be greater than 0." in result.stdout


def test_invalid_package_should_fail(tmp_path: Path):
    result = runner.invoke(app, f"install {MANIFEST_INVALID_PACKAGE} -w {tmp_path}")
    assert "ERR" in result.stdout


def test_invoke_from_python_m():
    import subprocess

    result = subprocess.run(
        ["python", "-m", "frontman", "install", "--help"],
        stdout=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert "Usage: frontman install [OPTIONS] [MANIFEST_PATH]" in result.stdout.decode()


@pytest.mark.parametrize(
    "arguments, expected_timeout", [([], 30.0), (["--timeout", "2.5"], 2.5)]
)
def test_timeout_option_reaches_downloader(monkeypatch, arguments, expected_timeout):
    downloader = Mock(return_value=iter(()))
    monkeypatch.setattr("frontman.main.download_concurrent", downloader)

    result = runner.invoke(app, ["install", str(MANIFEST_OK)] + arguments)

    assert result.exit_code == 0, result.output
    assert downloader.call_count == 1
    assert downloader.call_args[1]["timeout"] == expected_timeout


@pytest.mark.parametrize("timeout", ["0", "-1", "nan", "inf", "-inf", "invalid"])
def test_invalid_timeout_is_rejected(monkeypatch, timeout):
    downloader = Mock()
    monkeypatch.setattr("frontman.main.download_concurrent", downloader)

    result = runner.invoke(app, ["install", str(MANIFEST_OK), "--timeout", timeout])

    assert result.exit_code == 2
    assert "--timeout" in result.output
    downloader.assert_not_called()


def test_timeout_is_reported_as_download_error(tmp_path, monkeypatch):
    request = Mock(side_effect=requests.ReadTimeout("Read timed out"))
    monkeypatch.setattr(requests.Session, "get", request)

    result = runner.invoke(
        app, ["install", str(MANIFEST_OK), "-w", str(tmp_path), "--timeout", "0.5"]
    )

    assert result.output.count("ERR") == 4
    assert result.output.count("Read timed out") == 4
    assert request.call_count == 4
    assert all(item[1]["timeout"] == 0.5 for item in request.call_args_list)
