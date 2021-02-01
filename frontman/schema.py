from pathlib import Path
from typing import List, Optional, Union

from pydantic import BaseModel

from .provider import ProviderEnum


class PackageFile(BaseModel):
    name: str
    destination: Optional[Path] = Path('')
    rename: Optional[str]


class Package(BaseModel):
    name: str
    version: str
    path: Optional[Path]
    files: List[Union[str, PackageFile]]
    destination: Optional[Path]
    provider: Optional[ProviderEnum]


class Manifest(BaseModel):
    provider: ProviderEnum = ProviderEnum.CDNJS
    destination: Path
    packages: List[Package]
