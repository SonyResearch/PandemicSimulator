# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import Optional

import numpy as np

from .base_business import AgeRestrictedBusinessBaseLocation
from ..interfaces import Registry, LocationID, NonEssentialBusinessLocationState

__all__ = ['Bar']


class Bar(AgeRestrictedBusinessBaseLocation):
    """Implements a Bar"""

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
        super().__init__(age_limits=(21, 65), registry=registry, name=name, road_id=road_id, init_state=init_state,
                         numpy_rng=numpy_rng)
        
