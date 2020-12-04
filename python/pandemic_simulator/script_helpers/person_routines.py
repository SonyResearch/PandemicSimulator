# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

"""This helper module contains a few standard routines for persons in the simulator."""

from typing import Sequence, Type, Optional

import numpy as np

from ..environment import LocationID, PersonRoutine, Registry, SimTimeInterval, GroceryStore, \
    RetailStore, HairSalon, Retired, Restaurant, Bar, SimTimeTuple

__all__ = ['get_minor_routines', 'get_adult_routines', 'get_during_work_routines',
           'triggered_routine', 'weekend_routine', 'mid_day_during_week_routine']


def triggered_routine(location_type: type,
                      registry: Registry,
                      interval_in_days: int,
                      numpy_rng: np.random.RandomState,
                      start_loc: Optional[LocationID] = None,
                      explore_probability: float = 0.05) -> PersonRoutine:
    locations = registry.location_ids_of_type(location_type)
    assert len(locations) > 0
    return PersonRoutine(start_loc=start_loc,
                         end_loc=locations[numpy_rng.randint(0, len(locations))],
                         start_time=SimTimeInterval(day=interval_in_days,
                                                    offset_day=numpy_rng.randint(0, interval_in_days)),
                         explore_probability=explore_probability)


def weekend_routine(location_type: type,
                    registry: Registry,
                    numpy_rng: np.random.RandomState,
                    start_loc: Optional[LocationID] = None,
                    explore_probability: float = 0.05) -> PersonRoutine:
    locations = registry.location_ids_of_type(location_type)
    assert len(locations) > 0
    return PersonRoutine(start_loc=start_loc,
                         end_loc=locations[numpy_rng.randint(0, len(locations))],
                         start_time=SimTimeTuple(week_days=(5, 6)),
                         explore_probability=explore_probability)


def mid_day_during_week_routine(location_type: type,
                                registry: Registry,
                                numpy_rng: np.random.RandomState,
                                start_loc: Optional[LocationID] = None,
                                explore_probability: float = 0.05) -> PersonRoutine:
    locations = registry.location_ids_of_type(location_type)
    assert len(locations) > 0
    return PersonRoutine(start_loc=start_loc,
                         end_loc=locations[numpy_rng.randint(0, len(locations))],
                         start_time=SimTimeTuple(hours=(11, 2), week_days=tuple(range(0, 5))),
                         explore_probability=explore_probability)


def get_minor_routines(home_id: LocationID,
                       registry: Registry,
                       numpy_rng: Optional[np.random.RandomState] = None) -> Sequence[PersonRoutine]:
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()
    routines = [
        triggered_routine(HairSalon, registry, 30, numpy_rng, home_id),
        weekend_routine(Restaurant, registry, numpy_rng, home_id, explore_probability=0.3),
    ]
    return routines


def get_adult_routines(person_type: Type,
                       home_id: LocationID,
                       registry: Registry,
                       numpy_rng: Optional[np.random.RandomState] = None) -> Sequence[PersonRoutine]:
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

    routines = [
        triggered_routine(GroceryStore, registry, 7, numpy_rng),
        triggered_routine(RetailStore, registry, 7, numpy_rng),
        triggered_routine(HairSalon, registry, 30, numpy_rng),
        weekend_routine(Restaurant, registry, numpy_rng, home_id, explore_probability=0.5),
    ]
    if isinstance(person_type, Retired):
        routines.append(triggered_routine(Bar, registry, 2, numpy_rng, home_id, explore_probability=0.2))
    else:
        routines.append(triggered_routine(Bar, registry, 3, numpy_rng, home_id, explore_probability=0.5))

    return routines


def get_during_work_routines(registry: Registry,
                             numpy_rng: Optional[np.random.RandomState] = None) -> Sequence[PersonRoutine]:
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

    routines = [
        mid_day_during_week_routine(Restaurant, registry, numpy_rng),  # ~cafeteria  during work
    ]

    return routines
