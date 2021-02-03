import json
from pathlib import Path

from frontman.process import generate_file_list
from frontman.schema import Manifest

MANIFEST = """{
  "provider": "jsdelivr",
  "destination": "assets",
  "packages": [
    {
      "name": "jquery",
      "version": "3.5.1",
      "provider": "cdnjs",
      "files": [
        {
          "name": "jquery.min.js",
          "destination": "jquery"
        }
      ]
    },
    {
      "name": "@popperjs/core",
      "version": "2.6.0",
      "path": "dist/umd",
      "destination":"popper",
      "files": [
        {
          "name": "popper.min.js",
          "rename": "popper.js"
        }
      ]
    },
    {
      "name": "bootstrap",
      "version": "4.6.0",
      "provider": "unpkg",
      "path": "dist",
      "destination": "bootstrap",
      "files": [
        "js/bootstrap.min.js",
        "css/bootstrap.min.css"
      ]
    }
  ]
}
"""


def test_generate_file_list():
    root_path = Path.cwd()
    manifest = Manifest.parse_obj(json.loads(MANIFEST))

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
