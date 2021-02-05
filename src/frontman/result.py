from abc import ABC
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Result(ABC):
    source: str


@dataclass
class SuccessResult(Result):
    destination: Path
    skip: bool = False


@dataclass
class ErrorResult(Result):
    error: Exception
