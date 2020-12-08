# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import Optional

import numpy as np

from .base_business import AgeRestrictedBusinessBaseLocation
from ..interfaces import Registry, LocationID, NonEssentialBusinessLocationState, PersonID

__all__ = ['School']


class School(AgeRestrictedBusinessBaseLocation):
    """Implements a school"""

    def __init__(self, registry: Registry,
                 name: Optional[str] = None,
                 road_id: Optional[LocationID] = None,
                 init_state: Optional[NonEssentialBusinessLocationState] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param registry: Registry instance to register the location and handle people exit from location
        :param name: Name of the location
        :param road_id: id of the road connected to the location
        :param init_state: Optional initial state of the location. Set to default if None
        :param numpy_rng: Random number generator
        """
        super().__init__(age_limits=(2, 18), registry=registry, name=name, road_id=road_id, init_state=init_state,
                         numpy_rng=numpy_rng)

    def is_entry_allowed(self, person_id: PersonID) -> bool:
        if person_id in self._state.assignees:
            return True

        if self._age_limits[0] <= person_id.age <= self._age_limits[1]:
            return super().is_entry_allowed(person_id)

        return False
