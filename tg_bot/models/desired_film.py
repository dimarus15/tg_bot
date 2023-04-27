"""
Модель записи о желаемом к просмотру фильме
"""
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterator

from ..repository.abstract_repository import AbstractRepository

@dataclass(slots = True)
class DesiredFilm:

    title: str
    release_year: int
    priority: int
    pk: int = 0
