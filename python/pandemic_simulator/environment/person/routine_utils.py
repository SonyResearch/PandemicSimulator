# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from dataclasses import dataclass
from typing import Sequence, Optional, cast

import numpy as np

from .base import BasePerson
from ..interfaces import SimTime, SimTimeTuple, PersonRoutine, \
    SimTimeInterval, NoOP, NOOP, RepeatablePersonRoutine, LocationID, SpecialEndLoc

__all__ = ['RoutineWithStatus', 'execute_routines']


@dataclass
class RoutineWithStatus:
    """A mutable dataclass that maintains status variables of a routine to make it stateful."""

    routine: PersonRoutine
    due: bool = False
    started: bool = False
    duration: int = 0
    done: bool = False
    end_loc_selected: Optional[LocationID] = None
    """The final end_loc selected after sampling from routine.explorable_end_locs"""

    def _is_routine_due(self, sim_time: SimTime) -> bool:
        if self.started or self.done:
            # not due if the routine has already started or is completed
            return False

        if isinstance(self.routine.start_time, SimTimeTuple):
            return sim_time in self.routine.start_time
        elif isinstance(self.routine.start_time, SimTimeInterval):
            return self.due or self.routine.start_time.trigger_at_interval(sim_time)
        else:
            raise ValueError(f'Unrecognized type of start_time specified. {type(self.routine.start_time)}')

    def sync(self, sim_time: SimTime) -> None:
        """Sync the status variables with time."""
        # if completed check if you need to reset the routine for a repetition
        if (isinstance(self.routine, RepeatablePersonRoutine) and
                self.done and
                self.routine.repeat_interval_when_done.trigger_at_interval(sim_time)):
            self.reset()

        self.due = self._is_routine_due(sim_time)

    def reset(self) -> None:
        """Reset status variables"""
        self.due = False
        self.started = False
        self.duration = 0
        self.done = False
        self.end_loc_selected = None


def execute_routines(person: BasePerson,
                     routines_with_status: Sequence[RoutineWithStatus],
                     numpy_rng: np.random.RandomState) -> Optional[NoOP]:
    """
    Executes the given routines of the person in the simulator.
    Note that this function updates (mutates) status flags in the routines_with_status instances.

    :param person: person to execute the routine
    :param routines_with_status: a sequence of RoutineWithStatus instances
    :param numpy_rng: random number generator
    :return: returns a NOOP if none of the routines were executed (typically happens when the routines
        conditions are not met), otherwise None.
    """
    # the overall flow is that if a routine is due, start it and block the execution of other routines
    # until it has completed

    # first check if there are any ongoing routines that need to be completed
    for rws in routines_with_status:
        if rws.started and not rws.done:
            assert rws.end_loc_selected
            if (
                    # person left the end_location typically if the location closed due to external factors
                    (person.state.current_location != rws.end_loc_selected) or

                    # duration elapsed
                    (rws.duration >= rws.routine.duration_of_stay_at_end_loc)
            ):
                rws.done = True
            else:
                # block execution of other routines until the routine is complete
                return None

    # at this point there are no ongoing routines, now start the next routine that is due
    for rws in routines_with_status:
        routine = rws.routine
        if rws.due:
            assert not rws.started
            assert not rws.done
            if (
                    # check if we are in the correct location to start the routine
                    (routine.start_loc is None or routine.start_loc == person.state.current_location) and

                    # randomized start probability
                    numpy_rng.uniform() < routine.start_hour_probability
            ):
                # get the end location
                if routine.end_loc == SpecialEndLoc.social:
                    end_loc = person.get_social_gathering_location()
                    if end_loc is None:
                        # no social gatherings to attend, skip routine
                        continue
                else:
                    end_loc = cast(LocationID, routine.end_loc)

                if (len(routine.explorable_end_locs) > 0) and (numpy_rng.uniform() < routine.explore_probability):
                    end_loc = routine.explorable_end_locs[numpy_rng.randint(0, len(routine.explorable_end_locs))]
                assert end_loc
                if person.enter_location(end_loc):
                    # successfully entered the end location
                    rws.due = False
                    rws.started = True
                    rws.duration = 1
                    rws.end_loc_selected = end_loc
                    return None
    return NOOP
