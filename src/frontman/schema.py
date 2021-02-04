from pathlib import Path
from typing import List, Optional, Union

from pydantic import BaseModel

from .provider import Provider


class PackageFile(BaseModel):
    name: str
    destination: Path = Path("")
    rename: Optional[str] = None


class Package(BaseModel):
    name: str
    version: str
    path: Optional[Path] = None
    destination: Optional[Path] = None
    provider: Optional[Provider] = None
    files: List[Union[str, PackageFile]]


class Manifest(BaseModel):
    provider: Provider
    destination: Path
    packages: List[Package]
