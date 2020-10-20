# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from dataclasses import dataclass
from typing import Union, Optional

from .location_states import ContactRate
from .sim_time import SimTimeTuple
from .pandemic_types import Default

__all__ = ['LocationRule', 'BusinessLocationRule', 'NonEssentialBusinessLocationRule']


@dataclass(frozen=True)
class LocationRule:
    """A rule to modify the location's operation."""
    contact_rate: Union[ContactRate, Default, None] = None
    visitor_time: Union[SimTimeTuple, Default, None] = None
    visitor_capacity: Union[Default, int, None] = None


@dataclass(frozen=True)
class BusinessLocationRule(LocationRule):
    open_time: Union[SimTimeTuple, Default, None] = None


@dataclass(frozen=True)
class NonEssentialBusinessLocationRule(BusinessLocationRule):
    lock: Optional[bool] = None
