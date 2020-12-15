# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import Optional

import numpy as np

from .base_business import AgeRestrictedBusinessBaseLocation, NonEssentialBusinessBaseLocation
from ..interfaces import Registry, LocationID, NonEssentialBusinessLocationState, ContactRate, SimTimeTuple

__all__ = ['Bar', 'Restaurant']


class RestaurantState(NonEssentialBusinessLocationState):
    contact_rate: ContactRate = ContactRate(1, 1, 0, 0.3, 0.35, 0.1)
    open_time: SimTimeTuple = SimTimeTuple(hours=tuple(range(11, 16)) + tuple(range(19, 24)),
                                           week_days=tuple(range(1, 7)))


class Restaurant(NonEssentialBusinessBaseLocation[RestaurantState]):
    """Implements a restaurant location."""

    def create_state(self) -> RestaurantState:
        return RestaurantState()


class Bar(AgeRestrictedBusinessBaseLocation):
    """Implements a Bar"""

    def __init__(self,
                 loc_id: LocationID,
                 registry: Registry,
                 road_id: Optional[LocationID] = None,
                 init_state: Optional[NonEssentialBusinessLocationState] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param loc_id: Location ID instance.
        :param registry: Registry instance to register the location and handle people exit from location
        :param road_id: id of the road connected to the location
        :param init_state: Optional initial state of the location. Set to default if None
        :param numpy_rng: Random number generator
        """
        super().__init__(age_limits=(21, 110), registry=registry, loc_id=loc_id, road_id=road_id, init_state=init_state,
                         numpy_rng=numpy_rng)
