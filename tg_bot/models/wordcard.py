"""
Модель карточки со словом
"""
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterator

from ..repository.abstract_repository import AbstractRepository


@dataclass(slots = True)
class WordCard:

    word: str
    translation: str
    pk: int = 0
