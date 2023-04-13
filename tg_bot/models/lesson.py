"""
Модель класса урока
"""
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterator

from ..repository.abstract_repository import AbstractRepository


@dataclass(slots = True)
class Lesson:

    number: int
    difficulty: int
    pk: int = 0
