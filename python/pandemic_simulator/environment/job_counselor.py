# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

import numpy as np

from .city_registry import CityRegistry
from .interfaces import LocationID
from .location import BusinessBaseLocation

__all__ = ['JobCounselor', 'LocationParams', 'PopulationParams']


@dataclass(frozen=True)
class LocationParams:
    num: int
    worker_capacity: int = -1
    visitor_capacity: int = -1


@dataclass
class PopulationParams:
    num_persons: int
    location_type_to_params: Dict[type, LocationParams]
    viz_scale: int = 2


class JobCounselor:
    _all_work_ids_vacant_pos: List[Tuple[List[LocationID], int]]
    _numpy_rng: np.random.RandomState

    def __init__(self,
                 population_params: PopulationParams,
                 registry: CityRegistry,
                 numpy_rng: Optional[np.random.RandomState] = None):
        self._all_work_ids_vacant_pos = [(registry.location_ids_of_type(loc_type), params.num * params.worker_capacity)
                                         for loc_type, params in population_params.location_type_to_params.items()
                                         if issubclass(loc_type, BusinessBaseLocation)]
        self._numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

    def next_available_work_id(self) -> Optional[LocationID]:
        if len(self._all_work_ids_vacant_pos) == 0:
            return None

        work_type_index = self._numpy_rng.randint(0, len(self._all_work_ids_vacant_pos))
        work_ids, vacant_positions = self._all_work_ids_vacant_pos[work_type_index]

        work_id: LocationID = work_ids[self._numpy_rng.randint(0, len(work_ids))]
        vacant_positions -= 1

        if vacant_positions <= 0:
            self._all_work_ids_vacant_pos.pop(work_type_index)
        else:
            self._all_work_ids_vacant_pos[work_type_index] = (work_ids, vacant_positions)
        return work_id
