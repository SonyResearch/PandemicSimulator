# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from abc import ABCMeta
from typing import cast, Tuple, Optional, Type, TypeVar

import numpy as np

from .base import BaseLocation
from ..interfaces import SimTime, SimTimeTuple, Registry, PersonID, LocationID, LocationRule, DEFAULT, \
    BusinessLocationRule, BusinessLocationState, NonEssentialBusinessLocationState, \
    NonEssentialBusinessLocationRule

__all__ = ['BusinessBaseLocation', 'EssentialBusinessBaseLocation', 'NonEssentialBusinessBaseLocation',
           'AgeRestrictedBusinessBaseLocation']

_T = TypeVar('_T', bound=BusinessLocationState)
_T1 = TypeVar('_T1', bound=NonEssentialBusinessLocationState)


class BusinessBaseLocation(BaseLocation[_T], metaclass=ABCMeta):
    """Class that implements a base business location that has finite open hours."""

    location_rule_type: Type = BusinessLocationRule

    def update_rules(self, new_rule: LocationRule) -> None:
        super().update_rules(new_rule)
        rule = cast(BusinessLocationRule, new_rule)

        if rule.open_time is not None:
            self._state.open_time = (self._init_state.open_time if rule.open_time == DEFAULT
                                     else cast(SimTimeTuple, rule.open_time))


class EssentialBusinessBaseLocation(BusinessBaseLocation, metaclass=ABCMeta):
    """Class that implements an essential business location that has finite open hours."""
    pass


class NonEssentialBusinessBaseLocation(BusinessBaseLocation[_T], metaclass=ABCMeta):
    """Class that implements a non essential base business location that has finite open hours."""

    location_rule_type: Type = NonEssentialBusinessLocationRule

    def sync(self, sim_time: SimTime) -> None:
        super().sync(sim_time)
        self._state.is_open = False if self._state.locked else sim_time in self._state.open_time

    def update_rules(self, new_rule: LocationRule) -> None:
        super().update_rules(new_rule)
        rule = cast(NonEssentialBusinessLocationRule, new_rule)

        if rule.lock is not None:
            self._state.locked = rule.lock


class AgeRestrictedBusinessBaseLocation(NonEssentialBusinessBaseLocation[_T], metaclass=ABCMeta):
    """Class that implements a base age-restricted business location."""

    _age_limits: Tuple[int, int]

    def __init__(self, age_limits: Tuple[int, int],
                 loc_id: LocationID,
                 registry: Optional[Registry] = None,
                 road_id: Optional[LocationID] = None,
                 init_state: Optional[_T] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param age_limits: min and max age of allowed persons
        :param loc_id: Location ID
        :param registry: Registry instance to register the location and handle people exit from location. If None,
            the package wide registry instance is used.
        :param road_id: id of the road connected to the location
        :param init_state: Optional initial state of the location. Set to default if None
        :param numpy_rng: Random number generator
        """
        self._age_limits = age_limits
        super().__init__(registry=registry, loc_id=loc_id, road_id=road_id, init_state=init_state, numpy_rng=numpy_rng)

    def is_entry_allowed(self, person_id: PersonID) -> bool:
        if self._age_limits[0] <= person_id.age <= self._age_limits[1]:
            return super().is_entry_allowed(person_id)

        return False
