# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import cast, Tuple, Optional, Type

import numpy as np

from .base import BaseLocation
from ..interfaces import SimTime, SimTimeTuple, Registry, PersonID, LocationID, LocationRule, DEFAULT, \
    BusinessLocationRule, BusinessLocationState, NonEssentialBusinessLocationState, \
    NonEssentialBusinessLocationRule
from ...utils import checked_cast

__all__ = ['BusinessBaseLocation', 'EssentialBusinessBaseLocation', 'NonEssentialBusinessBaseLocation',
           'AgeRestrictedBusinessBaseLocation']


class BusinessBaseLocation(BaseLocation):
    """Class that implements a base business location that has finite open hours."""

    location_rule_type: Type = BusinessLocationRule

    def __init__(self, registry: Registry,
                 loc_id: LocationID,
                 road_id: Optional[LocationID] = None,
                 init_state: Optional[BusinessLocationState] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param registry: Registry instance to register the location and handle people exit from location
        :param loc_id: Location ID
        :param road_id: id of the road connected to the location
        :param init_state: Optional initial state of the location. Set to default if None
        :param numpy_rng: Random number generator
        """
        init_state = (checked_cast(BusinessLocationState, init_state) or BusinessLocationState(is_open=True))
        super().__init__(registry=registry, loc_id=loc_id, road_id=road_id, init_state=init_state, numpy_rng=numpy_rng)

    def update_rules(self, new_rule: LocationRule) -> None:
        super().update_rules(new_rule)
        init_state = cast(BusinessLocationState, self._init_state)
        state = cast(BusinessLocationState, self._state)
        rule = cast(BusinessLocationRule, new_rule)

        if rule.open_time is not None:
            state.open_time = init_state.open_time if rule.open_time == DEFAULT else cast(SimTimeTuple, rule.open_time)


class EssentialBusinessBaseLocation(BusinessBaseLocation):
    """Class that implements an essential business location that has finite open hours."""
    pass


class NonEssentialBusinessBaseLocation(BusinessBaseLocation):
    """Class that implements a non essential base business location that has finite open hours."""

    location_rule_type: Type = NonEssentialBusinessLocationRule

    def __init__(self, registry: Registry,
                 loc_id: LocationID,
                 road_id: Optional[LocationID] = None,
                 init_state: Optional[NonEssentialBusinessLocationState] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param registry: Registry instance to register the location and handle people exit from location
        :param loc_id: Location ID
        :param road_id: id of the road connected to the location
        :param init_state: Optional initial state of the location. Set to default if None
        :param numpy_rng: Random number generator
        """
        init_state = checked_cast(NonEssentialBusinessLocationState, init_state or
                                  NonEssentialBusinessLocationState(is_open=True))
        super().__init__(registry=registry, loc_id=loc_id, road_id=road_id, init_state=init_state, numpy_rng=numpy_rng)

    def sync(self, sim_time: SimTime) -> None:
        super().sync(sim_time)
        state = cast(NonEssentialBusinessLocationState, self._state)
        state.is_open = False if state.locked else sim_time in state.open_time

    def update_rules(self, new_rule: LocationRule) -> None:
        super().update_rules(new_rule)
        state = cast(NonEssentialBusinessLocationState, self._state)
        rule = cast(NonEssentialBusinessLocationRule, new_rule)

        if rule.lock is not None:
            state.locked = rule.lock


class AgeRestrictedBusinessBaseLocation(NonEssentialBusinessBaseLocation):
    """Class that implements a base age-restricted business location."""

    _age_limits: Tuple[int, int]

    def __init__(self, age_limits: Tuple[int, int],
                 registry: Registry,
                 loc_id: LocationID,
                 road_id: Optional[LocationID] = None,
                 init_state: Optional[NonEssentialBusinessLocationState] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param age_limits: min and max age of allowed persons
        :param registry: Registry instance to register the location and handle people exit from location
        :param loc_id: Location ID
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
