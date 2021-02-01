import os
from pathlib import Path

import json
import typer

from frontman.schema import Manifest
import frontman.process

CWD = Path(os.getcwd())

DEFAULT_MANIFEST = Path('frontman.json')
DEFAULT_THREADS = os.cpu_count() * 2


app = typer.Typer(name='FrontMan')


def success(file: str, dest: Path):
    typer.secho('OK  ', nl=False, fg=typer.colors.GREEN, bold=True)
    typer.echo(f'{file} -> {dest.relative_to(CWD)}')


def failure(file: str, ex: Exception):
    typer.secho('ERR ', nl=False, fg=typer.colors.RED, bold=True)
    typer.echo(f'{file}: {ex}', err=True)


@app.command()
def main(
        manifest: Path = typer.Option(DEFAULT_MANIFEST, help='Path to manifest file'),
        threads: int = typer.Option(DEFAULT_THREADS, help='Number of threads to use'),
):
    """Manage frontend dependencies"""
    if manifest is not None:
        if not manifest.exists():
            typer.echo('given manifest does not exist', err=True)
            raise typer.Exit(code=1)
        if not manifest.is_file():
            typer.echo('given manifest is not a file', err=True)
            raise typer.Exit(code=1)

        manifest_path = manifest.resolve()
    else:
        manifest_path = Path().resolve() / 'frontman.json'
        if not manifest_path.exists() or not manifest_path.is_file():
            typer.echo('not manifest found in current directory', err=True)
            raise typer.Exit(code=1)

    try:
        with open(manifest_path, 'r') as manifest_file:
            manifest_data = json.load(manifest_file)
        manifest = Manifest.parse_obj(manifest_data)
    except Exception as e:
        typer.echo(f'failed to parse manifest: {e}', err=True)
        raise typer.Exit(code=1)

    root_path = manifest_path.parent
    file_list = frontman.process.generate_file_list(root_path, manifest)
    frontman.process.download_concurrent(threads, file_list, success, failure)


def run():
    typer.run(main)


if __name__ == '__main__':
    run()
