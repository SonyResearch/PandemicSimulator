# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
import enum
from dataclasses import dataclass
from typing import Optional, Sequence, Union

from .ids import LocationID
from .sim_time import SimTimeInterval, SimTimeTuple

__all__ = ['PersonRoutine', 'SpecialEndLoc']


class SpecialEndLoc(enum.Enum):
    social = 0


@dataclass(frozen=True)
class PersonRoutine:
    """A dataclass that defines a person's routine every step (hour). """

    start_loc: Optional[LocationID]
    """Start location of the routine. If None, the routine can be started at any location."""

    end_loc: Union[LocationID, SpecialEndLoc]
    """End location of the routine that is either a specific location id or an instance of SpecialEndLoc."""

    valid_time: SimTimeTuple = SimTimeTuple()
    """Specifies the time during which the routine is available to start."""

    start_trigger_time: SimTimeInterval = SimTimeInterval(hour=1)
    """Start trigger time of the routine specified through SimTimeInterval. The routine will only start during
    valid_time, and once triggered the routine will be queued to be executed at some point while it remains valid.
    Default is set to be triggered to start every hour during valid_time."""

    start_hour_probability: float = 0.9
    """The probability for starting the routine around the trigger interval."""

    explorable_end_locs: Sequence[LocationID] = ()
    """A collection of end locations of the routine to explore with the probability given by
     `explore_probability`."""

    explore_probability: float = 0.05
    """Exploration probability to pick one of the explorable_end_locs instead of end_loc."""

    duration_of_stay_at_end_loc: int = 1
    """Specifies the duration (in hours) to stay at the end location."""

    repeat_interval_when_done: SimTimeInterval = SimTimeInterval(day=1)
    """Specifies the interval to repeat the routine when completed"""
