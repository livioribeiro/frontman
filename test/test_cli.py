import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from frontman.main import app
from frontman.result import ErrorResult, SuccessResult

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
    assert result.exit_code == 1
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
    "statuses, expected_exit_code",
    [
        ([], 0),
        (["OK", "OK"], 0),
        (["SKIP", "SKIP"], 0),
        (["OK", "SKIP"], 0),
        (["ERR", "ERR"], 1),
        (["ERR", "OK", "SKIP"], 1),
        (["OK", "ERR", "SKIP"], 1),
        (["SKIP", "OK", "ERR"], 1),
    ],
)
def test_install_reports_all_results_and_sets_exit_status(
    tmp_path, monkeypatch, statuses, expected_exit_code
):
    results = []
    expected_lines = []
    for index, status in enumerate(statuses):
        source = f"https://example.com/asset-{index}.js"
        destination = tmp_path / f"asset-{index}.js"
        if status == "ERR":
            error = OSError(f"Download {index} failed")
            results.append(ErrorResult(source, error))
            expected_lines.append(f"{status:<5}{source}: {error}")
        else:
            results.append(SuccessResult(source, destination, skip=status == "SKIP"))
            expected_lines.append(f"{status:<5}{source} -> {destination}")

    monkeypatch.setattr(
        "frontman.main.download_concurrent", lambda *args: iter(results)
    )

    result = runner.invoke(app, ["install", str(MANIFEST_OK), "-w", str(tmp_path)])

    assert result.stdout.splitlines() == expected_lines
    assert result.exit_code == expected_exit_code
