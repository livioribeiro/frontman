import os
from pathlib import Path

import pytest
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
    assert "Manifest must be in JSON or TOML format." in result.stdout


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


@pytest.fixture
def download_plans(monkeypatch):
    plans = []

    def capture_downloads(file_list, force, concurrency):
        plans.append((list(file_list), force, concurrency))
        return ()

    monkeypatch.setattr("frontman.main.download_concurrent", capture_downloads)
    return plans


def test_toml_and_json_produce_same_download_plan(tmp_path, download_plans):
    for manifest_path in (MANIFEST_OK, MANIFEST_OK.with_suffix(".toml")):
        result = runner.invoke(
            app, ["install", str(manifest_path), "-w", str(tmp_path), "-f", "-c", "2"]
        )
        assert result.exit_code == 0, result.output

    assert len(download_plans) == 2
    assert download_plans[0] == download_plans[1]
    assert len(download_plans[0][0]) == 4
    assert download_plans[0][1:] == (True, 2)


def test_toml_uses_current_workdir(tmp_path, monkeypatch, download_plans):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["install", str(MANIFEST_OK.with_suffix(".toml"))])

    assert result.exit_code == 0, result.output
    assert download_plans[0][0][0][1] == tmp_path / "assets/jquery/jquery.min.js"


def test_default_manifest_remains_json(tmp_path, monkeypatch, download_plans):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "frontman.json").write_bytes(MANIFEST_OK.read_bytes())
    (tmp_path / "pyproject.toml").write_text("not valid TOML")

    result = runner.invoke(app, ["install"])

    assert result.exit_code == 0, result.output
    assert len(download_plans) == 1
    assert len(download_plans[0][0]) == 4


@pytest.mark.parametrize(
    "manifest_name, target_name",
    [
        ("frontman.toml", "manifest"),
        ("frontman.toml", "manifest.json"),
        ("frontman.json", "manifest.toml"),
    ],
)
def test_manifest_symlink_uses_supplied_extension(
    tmp_path, manifest_name, target_name, download_plans
):
    manifest_path = tmp_path / manifest_name
    target_path = tmp_path / target_name
    fixture_path = MANIFEST_OK.with_suffix(manifest_path.suffix)
    target_path.write_bytes(fixture_path.read_bytes())
    manifest_path.symlink_to(target_path)

    result = runner.invoke(app, ["install", str(manifest_path), "-w", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert len(download_plans) == 1
    assert len(download_plans[0][0]) == 4
    assert download_plans[0][0][0][1] == tmp_path / "assets/jquery/jquery.min.js"


@pytest.mark.parametrize(
    "manifest_text, message",
    [
        ("[tool.frontman", "Manifest contains invalid TOML"),
        ("", "Manifest must contain a [tool.frontman] table"),
        (
            '[project]\nname = "example"',
            "Manifest must contain a [tool.frontman] table",
        ),
        ("tool = false", "Manifest must contain a [tool.frontman] table"),
        ('[tool]\nfrontman = "wrong"', "Manifest must contain a [tool.frontman] table"),
        ("[[tool.frontman]]", "Manifest must contain a [tool.frontman] table"),
        ("[tool.frontman]", "Manifest is not in expected format"),
        (
            '[tool.frontman]\nprovider = "unknown"\n'
            'destination = "assets"\npackages = []',
            "Manifest is not in expected format",
        ),
        (
            '[tool.frontman]\nprovider = "jsdelivr"\ndestination = "assets"\n'
            '[[tool.frontman.packages]]\nname = "jquery"\nversion = "3.5.1"',
            "Manifest is not in expected format",
        ),
    ],
)
def test_invalid_toml_manifest_should_fail(
    tmp_path, manifest_text, message, download_plans
):
    manifest_path = tmp_path / "pyproject.toml"
    manifest_path.write_text(manifest_text, encoding="utf-8")

    result = runner.invoke(app, ["install", str(manifest_path)])

    assert result.exit_code == 1
    assert message in result.output
    assert download_plans == []
