import json
from pathlib import Path

from frontman.process import generate_file_list
from frontman.schema import Manifest


def test_generate_file_list():
    root_path = Path.cwd()
    manifest_file = Path(__file__).parent / "frontman.json"
    manifest_json = json.loads(manifest_file.read_bytes())
    manifest = Manifest.parse_obj(manifest_json)

    file_list = set(generate_file_list(root_path, manifest))

    assert len(file_list) == 4
    assert file_list == {
        (
            "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js",
            root_path / "assets/jquery/jquery.min.js",
        ),
        (
            "https://cdn.jsdelivr.net/npm/@popperjs/core@2.6.0/dist/umd/popper.min.js",
            root_path / "assets/popper/popper.js",
        ),
        (
            "https://unpkg.com/bootstrap@4.6.0/dist/js/bootstrap.min.js",
            root_path / "assets/bootstrap/js/bootstrap.min.js",
        ),
        (
            "https://unpkg.com/bootstrap@4.6.0/dist/css/bootstrap.min.css",
            root_path / "assets/bootstrap/css/bootstrap.min.css",
        ),
    }
