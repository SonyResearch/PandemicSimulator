# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

"""This helper module contains a few standard routines for persons in the simulator."""

from typing import Sequence, Type, Optional, Tuple

from ..environment import LocationID, PersonRoutine, SimTimeInterval, HairSalon, Restaurant, Bar, \
    SimTimeTuple, GroceryStore, RetailStore, SpecialEndLoc, globals

__all__ = ['get_minor_routines',
           'get_retired_routines',
           'get_worker_during_work_routines',
           'get_worker_outside_work_routines',
           'triggered_routine',
           'weekend_routine',
           'mid_day_during_week_routine']

"""
References:
https://www.touchbistro.com/blog/how-diners-choose-restaurants/

"""


def _get_locations_from_type(location_type: Type) -> Tuple[LocationID, Sequence[LocationID]]:
    assert globals.registry, 'No registry found. Create the repo wide registry first by calling init_globals()'
    explorable_end_locs = globals.registry.location_ids_of_type(location_type)
    assert len(explorable_end_locs) > 0, f'{location_type.__name__}'
    end_loc = explorable_end_locs[globals.numpy_rng.randint(0, len(explorable_end_locs))]
    return end_loc, explorable_end_locs


def triggered_routine(start_loc: Optional[LocationID],
                      end_location_type: type,
                      interval_in_days: int,
                      explore_probability: float = 0.05) -> PersonRoutine:
    end_loc, explorable_end_locs = _get_locations_from_type(end_location_type)
    return PersonRoutine(start_loc=start_loc,
                         end_loc=end_loc,
                         start_trigger_time=SimTimeInterval(day=interval_in_days,
                                                            offset_day=globals.numpy_rng.randint(0, interval_in_days)),
                         explorable_end_locs=explorable_end_locs,
                         explore_probability=explore_probability)


def weekend_routine(start_loc: Optional[LocationID],
                    end_location_type: type,
                    explore_probability: float = 0.05,
                    repeat_interval_when_done: SimTimeInterval = SimTimeInterval(day=1)) -> PersonRoutine:
    end_loc, explorable_end_locs = _get_locations_from_type(end_location_type)
    return PersonRoutine(start_loc=start_loc,
                         end_loc=end_loc,
                         valid_time=SimTimeTuple(week_days=(5, 6)),
                         explorable_end_locs=explorable_end_locs,
                         explore_probability=explore_probability,
                         repeat_interval_when_done=repeat_interval_when_done)


def mid_day_during_week_routine(start_loc: Optional[LocationID],
                                end_location_type: type,
                                explore_probability: float = 0.05) -> PersonRoutine:
    end_loc, explorable_end_locs = _get_locations_from_type(end_location_type)
    return PersonRoutine(start_loc=start_loc,
                         end_loc=end_loc,
                         valid_time=SimTimeTuple(hours=tuple(range(11, 14)), week_days=tuple(range(0, 5))),
                         explorable_end_locs=explorable_end_locs,
                         explore_probability=explore_probability)


def social_routine(start_loc: Optional[LocationID]) -> PersonRoutine:
    return PersonRoutine(start_loc=start_loc,
                         end_loc=SpecialEndLoc.social,
                         valid_time=SimTimeTuple(hours=tuple(range(15, 20))),
                         duration_of_stay_at_end_loc=globals.numpy_rng.randint(1, 3),
                         repeat_interval_when_done=SimTimeInterval(day=7))


def get_minor_routines(home_id: LocationID, age: int) -> Sequence[PersonRoutine]:
    routines = [
        triggered_routine(home_id, HairSalon, 30),
        weekend_routine(home_id, Restaurant, explore_probability=0.5),
    ]
    if age >= 12:
        routines.append(social_routine(home_id))

    return routines


def get_retired_routines(home_id: LocationID) -> Sequence[PersonRoutine]:
    routines = [
        triggered_routine(None, GroceryStore, 7),
        triggered_routine(None, RetailStore, 7),
        triggered_routine(None, HairSalon, 30),
        weekend_routine(None, Restaurant, explore_probability=0.5),
        triggered_routine(home_id, Bar, 2, explore_probability=0.5),
        social_routine(home_id)
    ]
    return routines


def get_worker_during_work_routines(work_id: LocationID) -> Sequence[PersonRoutine]:
    routines = [
        mid_day_during_week_routine(work_id, Restaurant),  # ~cafeteria  during work
    ]

    return routines


def get_worker_outside_work_routines(home_id: LocationID) -> Sequence[PersonRoutine]:
    routines = [
        triggered_routine(None, GroceryStore, 7),
        triggered_routine(None, RetailStore, 7),
        triggered_routine(None, HairSalon, 30),
        weekend_routine(None, Restaurant, explore_probability=0.5),
        triggered_routine(home_id, Bar, 3, explore_probability=0.5),
        social_routine(home_id)
    ]
    return routines
