import json
from pathlib import Path
from typing import Optional

import typer
from typer.colors import BLUE, CYAN, GREEN, RED

from frontman.download import download_concurrent
from frontman.process import generate_file_list
from frontman.result import Result, Status
from frontman.schema import Manifest

CURRENT_DIR = Path.cwd()

DEFAULT_MANIFEST = Path("./frontman.json")

STATUS_STYLE = {
    Status.OK: typer.style(f"{'OK':<5}", fg=GREEN, bold=True),
    Status.SKIP: typer.style(f"{'SKIP':<5}", fg=CYAN, bold=True),
    Status.ERROR: typer.style(f"{'ERR':<5}", fg=RED, bold=True),
}

app = typer.Typer(name="frontman")


@app.callback()
def callback():
    """Frontend Dependency Manager"""


def log_result(result: Result):
    src = result.source
    dest = result.destination

    if result.status == Status.ERROR:
        output = f"{src}: {result.error}"
    else:
        output = f"{src} -> {dest.relative_to(CURRENT_DIR)}"

    status = STATUS_STYLE[result.status]

    typer.echo(status + output)


def manifest_callback(value: Path):
    if not value.name.endswith(".json"):
        raise typer.BadParameter("Manifest must be in JSON format.")

    if not value.exists():
        raise typer.BadParameter(f"Manifest file '{value}' does not exist.")

    if value.is_dir():
        raise typer.BadParameter("Manifest must be a file.")

    return value.resolve()


def concurrency_callback(value: Optional[int]):
    if value is not None and value < 1:
        raise typer.BadParameter("Value must be greater than 0.")

    return value


@app.command(name="install")
def install(
    manifest_file: Path = typer.Argument(
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
):
    try:
        with open(manifest_file, "r") as file:
            manifest_data = json.load(file)
        manifest = Manifest.parse_obj(manifest_data)
    except Exception as e:
        typer.echo(f"failed to parse manifest: {e}", err=True)
        raise typer.Exit(code=1)

    root_path = manifest_file.parent
    file_list = generate_file_list(root_path, manifest)

    for result in download_concurrent(file_list, force, concurrency):
        log_result(result)
