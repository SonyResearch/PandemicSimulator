# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import Optional

import numpy as np

from .base import BaseLocation
from ..interfaces import Registry, LocationID, LocationState, ContactRate, \
    SimTime, SimTimeTuple, LocationRule

__all__ = ['Home']


class Home(BaseLocation):
    """Class that implements a standard Home location. """

    def __init__(self, registry: Registry,
                 name: Optional[str] = None,
                 visitor_capacity: int = -1,
                 road_id: Optional[LocationID] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param registry: Registry instance to register the location and handle people exit from location
        :param name: Name of the location.
        :param visitor_capacity: Maximum number of allowed visitors.
        :param road_id: id of the road connected to the location.
        :param numpy_rng: Random number generator
        """
        numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()
        self._social_event_time = SimTimeTuple(hours=tuple(range(15, 20)),
                                               days=tuple(numpy_rng.randint(0, 365, 12)))
        init_state = LocationState(is_open=True,
                                   visitor_capacity=visitor_capacity,
                                   contact_rate=ContactRate(0, 1, 0, 0.5, 0.3, 0.3),
                                   visitor_time=self._social_event_time)
        super().__init__(registry=registry, name=name, road_id=road_id, init_state=init_state, numpy_rng=numpy_rng)

    def sync(self, sim_time: SimTime) -> None:
        super().sync(sim_time)
        self._state.social_gathering_event = sim_time in self._social_event_time

    def update_rules(self, new_rule: LocationRule) -> None:
        pass
