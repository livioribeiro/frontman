import os
from pathlib import Path

from typer.testing import CliRunner

from frontman.main import app

runner = CliRunner()


def test_app_ok(tmp_path: Path):
    cwd = Path.cwd()
    os.chdir(tmp_path)

    manifest_path = Path(__file__).parent / 'frontman.json'

    result = runner.invoke(
        app, f"install {manifest_path} -w {tmp_path}"
    )

    os.chdir(cwd)

    assert result.exit_code == 0
    assert (tmp_path / "assets").exists()
    assert (tmp_path / "assets").is_dir()
    assert (tmp_path / "assets" / "jquery" / "jquery.min.js").is_file()


def test_workdir_ok(tmp_path: Path):
    manifest_path = Path(__file__).parent / 'frontman.json'

    result = runner.invoke(
        app, f"install {manifest_path} -w {tmp_path}"
    )

    assert result.exit_code == 0
    assert (tmp_path / "assets").exists()
    assert (tmp_path / "assets").is_dir()
    assert (tmp_path / "assets" / "jquery" / "jquery.min.js").is_file()


def test_invalid_manifest_file_type_should_fail():
    manifest_path = Path(__file__).parent / 'manifest.pdf'

    result = runner.invoke(
        app, f"install {manifest_path}"
    )

    assert result.exit_code != 0
    assert "Manifest must be in JSON format." in result.stdout


def test_invalid_manifest_format_should_fail():
    manifest_path = Path(__file__).parent / 'invalid.json'

    result = runner.invoke(
        app, f"install {manifest_path}"
    )

    assert result.exit_code != 0
    assert "Manifest contains invalid JSON" in result.stdout


def test_invalid_manifest_schema_should_fail():
    manifest_path = Path(__file__).parent / 'invalid-schema.json'

    result = runner.invoke(
        app, f"install {manifest_path}"
    )

    assert result.exit_code != 0
    assert "Manifest is not in expected format" in result.stdout


def test_non_existent_manifest_should_fail():
    manifest_path = Path(__file__).parent / "does-not-exist.json"

    result = runner.invoke(
        app, f"install {manifest_path}"
    )

    assert result.exit_code != 0
    assert f"Manifest file '{manifest_path}' does not exist." in result.stdout


def test_manifest_as_dir_should_fail():
    manifest_path = Path(__file__).parent

    result = runner.invoke(
        app, f"install {manifest_path}"
    )

    assert result.exit_code != 0
    assert f"Given manifest '{manifest_path}' must be a file." in result.stdout


def test_non_positive_concurrency_value_should_fail():
    manifest_path = Path(__file__).parent / "frontman.json"

    result = runner.invoke(
        app, f"install {manifest_path} -c 0"
    )

    assert result.exit_code != 0
    assert "Value must be greater than 0." in result.stdout


def test_negative_concurrency_value_should_fail():
    manifest_path = Path(__file__).parent / "frontman.json"

    result = runner.invoke(
        app, f"install {manifest_path} -c -1"
    )

    assert result.exit_code != 0
    assert "Value must be greater than 0." in result.stdout


def test_invalid_package_should_fail(tmp_path: Path):
    manifest_path = Path(__file__).parent / 'invalid-package.json'
    result = runner.invoke(
        app, f"install {manifest_path} -w {tmp_path}"
    )
    assert "ERR" in result.stdout
