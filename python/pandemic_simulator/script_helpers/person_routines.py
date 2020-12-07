# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

"""This helper module contains a few standard routines for persons in the simulator."""

from typing import Sequence, Type, Optional

import numpy as np

from ..environment import LocationID, PersonRoutine, RepeatablePersonRoutine, \
    Registry, SimTimeInterval, GroceryStore, RetailStore, HairSalon, Retired, Restaurant, Bar, SimTimeTuple

__all__ = ['get_minor_routines', 'get_adult_routines', 'get_during_work_routines',
           'triggered_repeatable_routine', 'weekend_repeatable_routine', 'mid_day_during_week_repeatable_routine']


def triggered_repeatable_routine(registry: Registry,
                                 start_loc: Optional[LocationID],
                                 end_location_type: type,
                                 interval_in_days: int,
                                 numpy_rng: np.random.RandomState,
                                 explore_probability: float = 0.05) -> PersonRoutine:
    explorable_end_locs = registry.location_ids_of_type(end_location_type)
    assert len(explorable_end_locs) > 0
    end_loc = explorable_end_locs[numpy_rng.randint(0, len(explorable_end_locs))]
    return RepeatablePersonRoutine(start_loc=start_loc,
                                   end_loc=end_loc,
                                   start_time=SimTimeInterval(day=interval_in_days,
                                                              offset_day=numpy_rng.randint(0, interval_in_days)),
                                   explorable_end_locs=explorable_end_locs,
                                   explore_probability=explore_probability)


def weekend_repeatable_routine(registry: Registry,
                               start_loc: Optional[LocationID],
                               end_location_type: type,
                               numpy_rng: np.random.RandomState,
                               explore_probability: float = 0.05) -> PersonRoutine:
    explorable_end_locs = registry.location_ids_of_type(end_location_type)
    assert len(explorable_end_locs) > 0
    end_loc = explorable_end_locs[numpy_rng.randint(0, len(explorable_end_locs))]
    return RepeatablePersonRoutine(start_loc=start_loc,
                                   end_loc=end_loc,
                                   start_time=SimTimeTuple(week_days=(5, 6)),
                                   explorable_end_locs=explorable_end_locs,
                                   explore_probability=explore_probability)


def mid_day_during_week_repeatable_routine(registry: Registry,
                                           start_loc: Optional[LocationID],
                                           end_location_type: type,
                                           numpy_rng: np.random.RandomState,
                                           explore_probability: float = 0.05) -> PersonRoutine:
    explorable_end_locs = registry.location_ids_of_type(end_location_type)
    assert len(explorable_end_locs) > 0
    end_loc = explorable_end_locs[numpy_rng.randint(0, len(explorable_end_locs))]
    return RepeatablePersonRoutine(start_loc=start_loc,
                                   end_loc=end_loc,
                                   start_time=SimTimeTuple(hours=(11, 2), week_days=tuple(range(0, 5))),
                                   explorable_end_locs=explorable_end_locs,
                                   explore_probability=explore_probability)


def get_minor_routines(home_id: LocationID,
                       registry: Registry,
                       numpy_rng: Optional[np.random.RandomState] = None) -> Sequence[PersonRoutine]:
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()
    routines = [
        triggered_repeatable_routine(registry, home_id, HairSalon, 30, numpy_rng),
        weekend_repeatable_routine(registry, home_id, Restaurant, numpy_rng, explore_probability=0.3),
    ]
    return routines


def get_adult_routines(person_type: Type,
                       home_id: LocationID,
                       registry: Registry,
                       numpy_rng: Optional[np.random.RandomState] = None) -> Sequence[PersonRoutine]:
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

    routines = [
        triggered_repeatable_routine(registry, None, GroceryStore, 7, numpy_rng),
        triggered_repeatable_routine(registry, None, RetailStore, 7, numpy_rng),
        triggered_repeatable_routine(registry, None, HairSalon, 30, numpy_rng),
        weekend_repeatable_routine(registry, home_id, Restaurant, numpy_rng, explore_probability=0.5),
    ]
    if isinstance(person_type, Retired):
        routines.append(triggered_repeatable_routine(registry, home_id, Bar, 2, numpy_rng, explore_probability=0.2))
    else:
        routines.append(triggered_repeatable_routine(registry, home_id, Bar, 3, numpy_rng, explore_probability=0.5))

    return routines


def get_during_work_routines(work_id: LocationID,
                             registry: Registry,
                             numpy_rng: Optional[np.random.RandomState] = None) -> Sequence[PersonRoutine]:
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

    routines = [
        mid_day_during_week_repeatable_routine(registry, work_id, Restaurant, numpy_rng),  # ~cafeteria  during work
    ]

    return routines
