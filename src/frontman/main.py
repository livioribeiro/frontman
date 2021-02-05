import json
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Optional, Union

import pydantic
import typer
from typer.colors import CYAN, GREEN, RED

from frontman.download import download_concurrent
from frontman.process import generate_file_list
from frontman.result import ErrorResult, SuccessResult
from frontman.schema import Manifest

DEFAULT_MANIFEST = Path("./frontman.json")

STATUS_OK = typer.style(f"{'OK':<5}", fg=GREEN, bold=True)
STATUS_SKIP = typer.style(f"{'SKIP':<5}", fg=CYAN, bold=True)
STATUS_ERROR = typer.style(f"{'ERR':<5}", fg=RED, bold=True)

app = typer.Typer(name="frontman")


@app.callback()
def callback():
    """Frontend Dependency Manager"""


def log_result(result: Union[SuccessResult, ErrorResult], workdir: Path):
    current_dir = Path.cwd()
    src = result.source

    if isinstance(result, ErrorResult):
        status = STATUS_ERROR
        output = f"{src}: {result.error}"
    else:
        status = STATUS_SKIP if result.skip else STATUS_OK
        dest = result.destination
        if workdir == current_dir:
            output = f"{src} -> {dest.relative_to(workdir)}"
        else:
            output = f"{src} -> {dest}"

    typer.echo(status + output)


def manifest_callback(value: Path):
    if not value.exists():
        raise typer.BadParameter(f"Manifest file '{value}' does not exist.")

    if not value.is_file():
        raise typer.BadParameter(f"Given manifest '{value}' must be a file.")

    if not value.name.endswith(".json"):
        raise typer.BadParameter("Manifest must be in JSON format.")

    return value.resolve()


def concurrency_callback(value: Optional[int]):
    if value is not None and value < 1:
        raise typer.BadParameter("Value must be greater than 0.")

    return value


def workdir_callback(value: Optional[Path]):
    return value or Path.cwd()


@app.command(name="install")
def install(
    manifest_path: Path = typer.Argument(
        DEFAULT_MANIFEST,
        help="Path to manifest file",
        callback=manifest_callback,
    ),
    concurrency: Optional[int] = typer.Option(
        None,
        "--concurrency",
        "-c",
        help="Number of threads used to download files.",
        callback=concurrency_callback,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Whether to download packages that are already downloaded",
        show_default=False,
    ),
    workdir: Path = typer.Option(
        None,
        "--workdir",
        "-w",
        help="Download packages relative to the given directory",
        callback=workdir_callback,
    ),
):
    try:
        manifest_data = json.loads(manifest_path.read_text())
        manifest = Manifest.parse_obj(manifest_data)
    except JSONDecodeError:
        typer.echo("Error: Manifest contains invalid JSON", err=True)
        raise typer.Exit(code=1)
    except pydantic.ValidationError:
        typer.echo("Error: Manifest is not in expected format", err=True)
        raise typer.Exit(code=1)

    file_list = generate_file_list(workdir, manifest)

    for result in download_concurrent(file_list, force, concurrency):
        log_result(result, workdir)
