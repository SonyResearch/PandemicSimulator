# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import Optional, List, Sequence

import numpy as np

from .base import BasePerson
from ..interfaces import LocationID, SimTime, NoOP, NOOP, Registry, Risk, PersonState, PersonRoutine, SimTimeTuple, \
    ContactTracer

__all__ = ['Retired']


class Retired(BasePerson):
    """Class that implements a retired person"""

    _socializing_done: bool
    _to_social_at_hour_prob: float

    _routines: Sequence[PersonRoutine]
    _routines_due: List[bool]

    _to_home_hour_prob: float

    def __init__(self, age: int,
                 home: LocationID,
                 registry: Registry,
                 routines: Sequence[PersonRoutine] = (),
                 name: Optional[str] = None,
                 risk: Optional[Risk] = None,
                 night_hours: SimTimeTuple = SimTimeTuple(hours=tuple(range(0, 6)) + tuple(range(22, 24))),
                 regulation_compliance_prob: float = 1.0,
                 init_state: Optional[PersonState] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param age: Age of the person
        :param home: Home location id
        :param registry: Registry instance to register the person and handle peron's entry to a location
        :param routines: A sequence of person routines to run
        :param name: Optional name of the person
        :param risk: Optional health risk of the person
        :param night_hours: night hours - a person by default goes back home and stays at home
        :param regulation_compliance_prob: probability of complying to a regulation
        :param init_state: Optional initial state of the person
        :param numpy_rng: Random number generator
        """
        super().__init__(age=age,
                         home=home,
                         registry=registry,
                         name=name,
                         risk=risk,
                         night_hours=night_hours,
                         regulation_compliance_prob=regulation_compliance_prob,
                         init_state=init_state,
                         numpy_rng=numpy_rng)

        self._socializing_done = False
        self._to_social_at_hour_prob = 0.9

        self._routines = routines
        self._routines_due = [False] * len(self._routines)

        self._to_home_hour_prob = 0.5

    def _sync(self, sim_time: SimTime) -> None:
        for i, routine in enumerate(self._routines):
            self._routines_due[i] = self._routines_due[i] or routine.trigger_interval.trigger_at_interval(sim_time)

        if sim_time.week_day == 0:
            self._socializing_done = False

    def step(self, sim_time: SimTime, contact_tracer: Optional[ContactTracer] = None) -> Optional[NoOP]:
        step_ret = super().step(sim_time, contact_tracer)
        if step_ret != NOOP:
            return step_ret

        # execute due outside work routines
        for i, (routine, routine_due) in enumerate(zip(self._routines, self._routines_due)):
            if (routine_due and
                    (routine.start_loc is None or routine.start_loc == self._state.current_location) and
                    self._numpy_rng.uniform() < routine.trigger_hour_probability):
                end_loc = routine.end_loc
                if (len(routine.end_locs) > 0) and (self._numpy_rng.uniform() < routine.explore_probability):
                    end_loc = routine.end_locs[self._numpy_rng.randint(0, len(routine.end_locs))]

                if self.enter_location(end_loc):
                    self._routines_due[i] = False
                    return None

        # if at home go to a social event if you have not been this week
        if (self.at_home and
                not self._socializing_done and
                self._numpy_rng.uniform() < self._to_social_at_hour_prob):
            social_loc = self._get_social_gathering_location()
            if social_loc is not None and self.enter_location(social_loc):
                self._socializing_done = True
                return None

        # if not at home go home
        if not self.at_home and self._numpy_rng.uniform() < self._to_home_hour_prob:
            self.enter_location(self.home)
            return None

        return NOOP
