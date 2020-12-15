# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import Optional

import numpy as np

from .base_business import AgeRestrictedBusinessBaseLocation
from ..interfaces import Registry, LocationID, NonEssentialBusinessLocationState, ContactRate, SimTimeTuple

__all__ = ['Office', 'OfficeState']


class OfficeState(NonEssentialBusinessLocationState):
    contact_rate: ContactRate = ContactRate(2, 1, 0, 0.1, 0.01, 0.01)
    open_time: SimTimeTuple = SimTimeTuple(hours=tuple(range(9, 17)), week_days=tuple(range(0, 5)))


class Office(AgeRestrictedBusinessBaseLocation[OfficeState]):
    """Implements an office"""

    def __init__(self,
                 loc_id: LocationID,
                 registry: Optional[Registry] = None,
                 road_id: Optional[LocationID] = None,
                 init_state: Optional[OfficeState] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param loc_id: Location ID instance.
        :param registry: Registry instance to register the location and handle people exit from location
        :param road_id: id of the road connected to the location
        :param init_state: Optional initial state of the location. Set to default if None
        :param numpy_rng: Random number generator
        """
        super().__init__(age_limits=(18, 65), registry=registry, loc_id=loc_id, road_id=road_id, init_state=init_state,
                         numpy_rng=numpy_rng)

    def create_state(self) -> OfficeState:
        return OfficeState()

