# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import Optional

import numpy as np

from .base import BaseLocation
from ..interfaces import Registry, PersonID, LocationRule, LocationState, ContactRate, LocationID

__all__ = ['Road']


class Road(BaseLocation):
    """Class that implements a road. """

    def __init__(self, registry: Registry,
                 loc_id: LocationID,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param registry: Registry instance to register the location and handle people exit from location
        :param loc_id: Location ID instance.
        :param numpy_rng: Random number generator
        """
        init_state = LocationState(is_open=True, visitor_capacity=-1,
                                   contact_rate=ContactRate(0, 0, 0, 0, 0, 0))
        super().__init__(registry=registry, loc_id=loc_id, road_id=None, init_state=init_state, numpy_rng=numpy_rng)

    def update_rules(self, new_rule: LocationRule) -> None:
        pass

    def is_entry_allowed(self, person_id: PersonID) -> bool:
        return True

    def assign_person(self, person_id: PersonID) -> None:
        pass
