# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from copy import deepcopy
from typing import Optional, Type, cast

import numpy as np

from ..interfaces import Location, LocationState, PersonID, LocationID, Registry, LocationRule, DEFAULT, \
    SimTime, ContactRate, SimTimeTuple

__all__ = ['BaseLocation']


class BaseLocation(Location):
    """Class that implements a base location."""

    location_rule_type: Type = LocationRule

    _registry: Registry
    _init_state: LocationState
    _numpy_rng: np.random.RandomState

    _id: LocationID
    _state: LocationState
    _road_id: Optional[LocationID]
    _current_sim_time: SimTime

    def __init__(self,
                 registry: Registry,
                 loc_id: LocationID,
                 road_id: Optional[LocationID] = None,
                 init_state: Optional[LocationState] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param registry: Registry instance to register the location and handle people exit from location
        :param loc_id: Location ID
        :param road_id: id of the road connected to the location
        :param init_state: Optional initial state of the location. Set to default if None
        :param numpy_rng: Random number generator
        """
        self._registry = registry
        self._id = loc_id
        self._road_id = road_id
        self._init_state = init_state or LocationState(is_open=True)
        self._numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

        self._state = deepcopy(self._init_state)

        self._registry.register_location(self)

    @property
    def id(self) -> LocationID:
        return self._id

    @property
    def state(self) -> LocationState:
        return self._state

    @property
    def init_state(self) -> LocationState:
        return self._init_state

    @property
    def road_id(self) -> Optional[LocationID]:
        return self._road_id

    def sync(self, sim_time: SimTime) -> None:
        self._current_sim_time = sim_time

    def update_rules(self, new_rule: LocationRule) -> None:
        cr = new_rule.contact_rate
        if cr is not None:
            self._state.contact_rate = (self._init_state.contact_rate if cr == DEFAULT else cast(ContactRate, cr))

        if new_rule.visitor_time is not None:
            self._state.visitor_time = (self._init_state.visitor_time if new_rule.visitor_time == DEFAULT
                                        else cast(SimTimeTuple, new_rule.visitor_time))
        if new_rule.visitor_capacity is not None:
            self._state.visitor_capacity = (self._init_state.visitor_capacity if new_rule.visitor_capacity == DEFAULT
                                            else new_rule.visitor_capacity)

    def is_entry_allowed(self, person_id: PersonID) -> bool:
        allow_assignee = person_id in self._state.assignees

        allow_visitor = (self._current_sim_time in self._state.visitor_time and
                         (self._state.visitor_capacity == -1 or
                          len(self._state.visitors_in_location) < self._state.visitor_capacity))

        return self._state.is_open and (allow_assignee or allow_visitor)

    def assign_person(self, person_id: PersonID) -> None:
        self._state.assignees.add(person_id)

    def add_person_to_location(self, person_id: PersonID) -> None:
        if person_id in self._state.assignees:
            self._state.assignees_in_location.add(person_id)
        else:
            self._state.visitors_in_location.add(person_id)

    def remove_person_from_location(self, person_id: PersonID) -> None:
        if person_id in self._state.assignees_in_location:
            self._state.assignees_in_location.remove(person_id)
        elif person_id in self._state.visitors_in_location:
            self._state.visitors_in_location.remove(person_id)
        else:
            # person is not in location
            pass

    def reset(self) -> None:
        self._state = deepcopy(self._init_state)
