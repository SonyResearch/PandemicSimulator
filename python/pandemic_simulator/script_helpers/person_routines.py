# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

"""This helper module contains a few standard routines for persons in the simulator."""

from typing import Sequence, Type, Optional

import numpy as np

from ..environment import LocationID, PersonRoutine, Registry, SimTimeInterval, HairSalon, Retired, Restaurant, Bar, \
    SimTimeTuple, GroceryStore, RetailStore, SpecialEndLoc

__all__ = ['get_minor_routines', 'get_adult_routines', 'get_during_work_routines',
           'triggered_routine', 'weekend_routine', 'mid_day_during_week_routine']

"""
A few references for the numbers selected:
https://www.touchbistro.com/blog/how-diners-choose-restaurants/

"""


def triggered_routine(registry: Registry,
                      start_loc: Optional[LocationID],
                      end_location_type: type,
                      interval_in_days: int,
                      numpy_rng: np.random.RandomState,
                      explore_probability: float = 0.05,
                      repeat_interval_when_done: SimTimeInterval = SimTimeInterval(day=1)) -> PersonRoutine:
    explorable_end_locs = registry.location_ids_of_type(end_location_type)
    assert len(explorable_end_locs) > 0
    end_loc = explorable_end_locs[numpy_rng.randint(0, len(explorable_end_locs))]
    return PersonRoutine(start_loc=start_loc,
                         end_loc=end_loc,
                         start_time=SimTimeInterval(day=interval_in_days,
                                                    offset_day=numpy_rng.randint(0, interval_in_days)),
                         explorable_end_locs=explorable_end_locs,
                         explore_probability=explore_probability,
                         repeat_interval_when_done=repeat_interval_when_done)


def weekend_routine(registry: Registry,
                    start_loc: Optional[LocationID],
                    end_location_type: type,
                    numpy_rng: np.random.RandomState,
                    explore_probability: float = 0.05,
                    repeat_interval_when_done: SimTimeInterval = SimTimeInterval(day=1)) -> PersonRoutine:
    explorable_end_locs = registry.location_ids_of_type(end_location_type)
    assert len(explorable_end_locs) > 0
    end_loc = explorable_end_locs[numpy_rng.randint(0, len(explorable_end_locs))]
    return PersonRoutine(start_loc=start_loc,
                         end_loc=end_loc,
                         start_time=SimTimeTuple(week_days=(5, 6)),
                         explorable_end_locs=explorable_end_locs,
                         explore_probability=explore_probability,
                         repeat_interval_when_done=repeat_interval_when_done)


def mid_day_during_week_routine(registry: Registry,
                                start_loc: Optional[LocationID],
                                end_location_type: type,
                                numpy_rng: np.random.RandomState,
                                explore_probability: float = 0.05) -> PersonRoutine:
    explorable_end_locs = registry.location_ids_of_type(end_location_type)
    assert len(explorable_end_locs) > 0
    end_loc = explorable_end_locs[numpy_rng.randint(0, len(explorable_end_locs))]
    return PersonRoutine(start_loc=start_loc,
                         end_loc=end_loc,
                         start_time=SimTimeTuple(hours=tuple(range(11, 14)), week_days=tuple(range(0, 5))),
                         explorable_end_locs=explorable_end_locs,
                         explore_probability=explore_probability,
                         repeat_interval_when_done=SimTimeInterval(day=1))


def social_routine(start_loc: Optional[LocationID],
                   numpy_rng: np.random.RandomState) -> PersonRoutine:
    return PersonRoutine(start_loc=start_loc,
                         end_loc=SpecialEndLoc.social,
                         start_time=SimTimeTuple(hours=tuple(range(15, 20))),
                         repeat_interval_when_done=SimTimeInterval(day=7),
                         duration_of_stay_at_end_loc=numpy_rng.randint(1, 3))


def get_minor_routines(home_id: LocationID,
                       age: int,
                       registry: Registry,
                       numpy_rng: Optional[np.random.RandomState] = None) -> Sequence[PersonRoutine]:
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()
    routines = [
        triggered_routine(registry, home_id, HairSalon, 30, numpy_rng),
        weekend_routine(registry, home_id, Restaurant, numpy_rng, explore_probability=0.5,
                        repeat_interval_when_done=SimTimeInterval(day=10)),
    ]
    if age >= 12:
        routines.append(social_routine(home_id, numpy_rng))

    return routines


def get_adult_routines(person_type: Type,
                       home_id: LocationID,
                       registry: Registry,
                       numpy_rng: Optional[np.random.RandomState] = None) -> Sequence[PersonRoutine]:
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

    routines = [
        triggered_routine(registry, None, GroceryStore, 7, numpy_rng),
        triggered_routine(registry, None, RetailStore, 7, numpy_rng),
        triggered_routine(registry, None, HairSalon, 30, numpy_rng),
        weekend_routine(registry, None, Restaurant, numpy_rng, explore_probability=0.5)
    ]
    if person_type == Retired:
        routines.append(triggered_routine(registry, home_id, Bar, 2, numpy_rng, explore_probability=0.5))
    else:
        routines.append(triggered_routine(registry, home_id, Bar, 3, numpy_rng, explore_probability=0.5))

    routines.append(social_routine(home_id, numpy_rng))

    return routines


def get_during_work_routines(work_id: LocationID,
                             registry: Registry,
                             numpy_rng: Optional[np.random.RandomState] = None) -> Sequence[PersonRoutine]:
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

    routines = [
        mid_day_during_week_routine(registry, work_id, Restaurant, numpy_rng),  # ~cafeteria  during work
    ]

    return routines
