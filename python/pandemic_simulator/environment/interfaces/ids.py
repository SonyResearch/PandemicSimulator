# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from dataclasses import dataclass

__all__ = ['LocationID', 'PersonID']

from typing import Tuple


@dataclass(frozen=True)
class LocationID:
    name: str
    tags: Tuple[str, ...] = ()


@dataclass(frozen=True)
class PersonID:
    name: str
    age: int
