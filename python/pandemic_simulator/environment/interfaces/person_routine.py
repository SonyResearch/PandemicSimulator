# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from dataclasses import dataclass
from typing import Optional, Sequence

from .ids import LocationID
from .sim_time import SimTimeInterval

__all__ = ['PersonRoutine']


@dataclass(frozen=True)
class PersonRoutine:
    """A dataclass that defines a person's routine every step (hour). """

    start_loc: Optional[LocationID]
    """Start location of the routine. If None, the routine can be started at any location."""

    end_loc: LocationID
    """End location of the routine."""

    trigger_interval: SimTimeInterval
    """A sim time interval that specifies when to start the routine."""

    trigger_hour_probability: float = 0.5
    """The probability for starting the routine around the trigger interval."""

    end_locs: Sequence[LocationID] = ()
    """A collection of end locations of the routine to explore. """

    explore_probability: float = 0.05
    """Exploration probability"""
