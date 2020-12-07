# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from dataclasses import dataclass
from typing import Optional, Sequence, Union

from .ids import LocationID
from .sim_time import SimTimeInterval, SimTimeTuple

__all__ = ['PersonRoutine', 'RepeatablePersonRoutine']


@dataclass(frozen=True)
class PersonRoutine:
    """A dataclass that defines a person's routine every step (hour). """

    start_loc: Optional[LocationID]
    """Start location of the routine. If None, the routine can be started at any location."""

    end_loc: LocationID
    """End location of the routine."""

    start_time: Union[SimTimeInterval, SimTimeTuple]
    """Start time of the routine specified either as through SimTimeInterval object or SimTimeTuple.

    Use SimTimeInterval if you want to trigger the start of the routine. Once triggered the routine
    will be queued and executed at some point in the person's life time.

    Use SimTimeTuple if you want to queue the start of a routine within the specified times. The routine
    will not be executed outside the specified times.
    """

    start_hour_probability: float = 0.5
    """The probability for starting the routine around the trigger interval."""

    explorable_end_locs: Sequence[LocationID] = ()
    """A collection of end locations of the routine to explore with the probability given by
     `explore_probability`."""

    explore_probability: float = 0.05
    """Exploration probability to pick one of the explorable_end_locs instead of end_loc."""

    duration_of_stay_at_end_loc: int = 1
    """Specifies the duration (in hours) to stay at the end location."""


@dataclass(frozen=True)
class RepeatablePersonRoutine(PersonRoutine):
    """A repeatable person routine"""

    repeat_interval: SimTimeInterval = SimTimeInterval(day=1)
    """Specifies the interval to repeat the routine"""
