# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from dataclasses import dataclass
from typing import Type, Optional, cast

import numpy as np

from .base import BaseLocation
from ..interfaces import LocationID, LocationRule, LocationState, PersonID, Registry, ContactRate, \
    DEFAULT, SimTimeTuple

__all__ = ['Cemetery', 'CemeteryRule']


@dataclass(frozen=True)
class CemeteryRule(LocationRule):
    def __post_init__(self) -> None:
        if isinstance(self.contact_rate, ContactRate):
            assert self.contact_rate.min_assignees == 0
            assert self.contact_rate.min_assignees_visitors == 0
            assert self.contact_rate.fraction_assignees == 0
            assert self.contact_rate.fraction_assignees_visitors == 0


class Cemetery(BaseLocation):
    """Class that implements a cemetery location. """

    location_rule_type: Type = CemeteryRule

    def __init__(self, registry: Registry,
                 name: Optional[str] = None,
                 road_id: Optional[LocationID] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param registry: Registry instance to register the location and handle people exit from location
        :param name: Name of the location
        :param road_id: id of the road connected to the location
        :param numpy_rng: Random number generator
        """
        init_state = LocationState(is_open=True, visitor_capacity=-1,
                                   contact_rate=ContactRate(0, 0, 0, 0, 0, 0.05))
        super().__init__(registry=registry, name=name, road_id=road_id, init_state=init_state, numpy_rng=numpy_rng)

    def update_rules(self, new_rule: LocationRule) -> None:
        rule = cast(CemeteryRule, new_rule)
        cr = rule.contact_rate
        if cr is not None:
            self._state.contact_rate = (self._init_state.contact_rate if cr == DEFAULT
                                        else cast(ContactRate, cr))

        if rule.visitor_time is not None:
            self._state.visitor_time = (self._init_state.visitor_time if rule.visitor_time == DEFAULT
                                        else cast(SimTimeTuple, rule.visitor_time))
        if rule.visitor_capacity is not None:
            self._state.visitor_capacity = (self._init_state.visitor_capacity if rule.visitor_capacity == DEFAULT
                                            else rule.visitor_capacity)

    def remove_person_from_location(self, person_id: PersonID) -> None:
        if person_id in self._state.assignees_in_location:
            raise ValueError(f'Person {person_id} is already cremated. Cannot remove!')
        elif person_id in self._state.visitors_in_location:
            self._state.visitors_in_location.remove(person_id)
        else:
            raise ValueError(f'Person {person_id} not in location {self.id}')
