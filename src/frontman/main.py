import json
import os
from pathlib import Path

import typer
from typer.colors import BLUE, CYAN, GREEN, RED

from frontman.download import download_concurrent
from frontman.process import generate_file_list
from frontman.result import Result, Status
from frontman.schema import Manifest

CWD = Path.cwd()

DEFAULT_MANIFEST = Path("frontman.json")
DEFAULT_MAX_CONCURRENCY = 8
DEFAULT_CONCURRENCY = min(os.cpu_count() * 2, DEFAULT_MAX_CONCURRENCY)
DEFAULT_UPDATE = False

STATUS_STYLE = {
    Status.NEW: typer.style(f"{'NEW':<8}", fg=GREEN, bold=True),
    Status.UPGRADE: typer.style(f"{'UPGRADE':<8}", fg=BLUE, bold=True),
    Status.SKIP: typer.style(f"{'SKIP':<8}", fg=CYAN, bold=True),
    Status.ERROR: typer.style(f"{'ERROR':<8}", fg=RED, bold=True),
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
        output = f"{src} -> {dest.relative_to(CWD)}"

    status = STATUS_STYLE[result.status]

    typer.echo(status + output)


@app.command(name="install")
def install(
    manifest_file: Path = typer.Argument(
        DEFAULT_MANIFEST, help="Path to manifest file"
    ),
    concurrency: int = typer.Option(
        DEFAULT_CONCURRENCY,
        "--concurrency",
        "-c",
        help="Number of threads used to download files",
    ),
    upgrade: bool = typer.Option(
        DEFAULT_UPDATE,
        "--upgrade",
        "-U",
        help="Whether to download packages that are already downloaded",
    ),
):
    if manifest_file is not None:
        if not manifest_file.exists():
            typer.echo("given manifest does not exist", err=True)
            raise typer.Exit(code=1)
        if not manifest_file.is_file():
            typer.echo("given manifest is not a file", err=True)
            raise typer.Exit(code=1)

        manifest_path = manifest_file.resolve()
    else:
        manifest_path = CWD / "frontman.json"
        if not manifest_path.exists() or not manifest_path.is_file():
            typer.echo("manifest not found in current directory", err=True)
            raise typer.Exit(code=1)

    try:
        with open(manifest_path, "r") as file:
            manifest_data = json.load(file)
        manifest = Manifest.parse_obj(manifest_data)
    except Exception as e:
        typer.echo(f"failed to parse manifest: {e}", err=True)
        raise typer.Exit(code=1)

    root_path = manifest_path.parent
    file_list = generate_file_list(root_path, manifest)
    concurrency = min(concurrency, len(manifest.packages))

    for result in download_concurrent(concurrency, file_list, upgrade):
        log_result(result)
