"""
Модель карточки со словом
"""
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterator

from ..repository.abstract_repository import AbstractRepository


@dataclass()
class WatchedFilm:

    title: str
    release_year: int
    rate: int
    comment: str
    pk: int = 0
