from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class Status(Enum):
    NEW = 1
    UPGRADE = 2
    ERROR = 3
    SKIP = 4


@dataclass
class Result:
    status: Status
    source: str
    destination: Optional[Path]
    error: Optional[Exception] = None
