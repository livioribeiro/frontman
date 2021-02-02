import os
from pathlib import Path

import json
import typer

from frontman.schema import Manifest
import frontman.process

CWD = Path(os.getcwd())

DEFAULT_MANIFEST = Path('frontman.json')
DEFAULT_MAX_CONCURRENCY = 8
DEFAULT_CONCURRENCY = min(os.cpu_count() * 2, DEFAULT_MAX_CONCURRENCY)


app = typer.Typer(name='FrontMan')


def success(file: str, dest: Path):
    typer.secho('OK  ', nl=False, fg=typer.colors.GREEN, bold=True)
    typer.echo(f'{file} -> {dest.relative_to(CWD)}')


def failure(file: str, ex: Exception):
    typer.secho('ERR ', nl=False, fg=typer.colors.RED, bold=True)
    typer.echo(f'{file}: {ex}', err=True)


@app.command()
def main(
        manifest_file: Path = typer.Argument(
            DEFAULT_MANIFEST,
            help='Path to manifest file'
        ),
        concurrency: int = typer.Option(
            DEFAULT_CONCURRENCY,
            "--concurrency",
            "-c",
            help='Number of threads used to download files'
        ),
):
    """Frontend Library Manager"""

    if manifest_file is not None:
        if not manifest_file.exists():
            typer.echo('given manifest does not exist', err=True)
            raise typer.Exit(code=1)
        if not manifest_file.is_file():
            typer.echo('given manifest is not a file', err=True)
            raise typer.Exit(code=1)

        manifest_path = manifest_file.resolve()
    else:
        manifest_path = CWD / 'frontman.json'
        if not manifest_path.exists() or not manifest_path.is_file():
            typer.echo('manifest not found in current directory', err=True)
            raise typer.Exit(code=1)

    try:
        with open(manifest_path, 'r') as file:
            manifest_data = json.load(file)
        manifest_file = Manifest.parse_obj(manifest_data)
    except Exception as e:
        typer.echo(f'failed to parse manifest: {e}', err=True)
        raise typer.Exit(code=1)

    root_path = manifest_path.parent
    file_list = frontman.process.generate_file_list(root_path, manifest_file)
    frontman.process.download_concurrent(
        concurrency, file_list, success, failure)


def run():
    typer.run(main)
