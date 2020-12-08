# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from typing import Optional, Sequence, List

import numpy as np

from .base import BasePerson
from .routine_utils import RoutineWithStatus, execute_routines
from ..interfaces import PersonState, LocationID, Risk, Registry, SimTime, NoOP, SimTimeTuple, NOOP, PersonRoutine, \
    ContactTracer

__all__ = ['Worker']


class Worker(BasePerson):
    """Class that implements a basic worker."""

    _work: LocationID
    _work_time: SimTimeTuple
    _to_work_at_hour_prob: float
    _to_home_hour_prob: float

    _during_work_rs: List[RoutineWithStatus]
    _outside_work_rs: List[RoutineWithStatus]

    def __init__(self, age: int,
                 home: LocationID,
                 work: LocationID,
                 registry: Registry,
                 work_time: Optional[SimTimeTuple] = None,
                 during_work_routines: Sequence[PersonRoutine] = (),
                 outside_work_routines: Sequence[PersonRoutine] = (),
                 name: Optional[str] = None,
                 risk: Optional[Risk] = None,
                 night_hours: SimTimeTuple = SimTimeTuple(hours=tuple(range(0, 6))),
                 regulation_compliance_prob: float = 1.0,
                 init_state: Optional[PersonState] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param age: Age of the person
        :param home: Home location id
        :param work: Work location id
        :param registry: Registry instance to register the person and handle peron's entry to a location
        :param work_time: Work time specified in SimTimeTuples. Default - 9am-5pm and Mon-Fri
        :param during_work_routines: A sequence of person routines to run during work time
        :param outside_work_routines: A sequence of person routines to run outside work time
        :param name: Optional name of the person
        :param risk: Optional health risk of the person.
        :param night_hours: night hours - a person by default goes back home and stays at home
        :param regulation_compliance_prob: probability of complying to a regulation
        :param init_state: Optional initial state of the person
        :param numpy_rng: Random number generator
        """
        assert age >= 18, "Workers's age must be >= 18"
        self._work = work
        self._work_time = work_time or SimTimeTuple(hours=tuple(range(9, 18)), week_days=tuple(range(0, 5)))
        self._to_work_at_hour_prob = 0.95
        self._to_home_hour_prob = 0.95
        self._during_work_rs = [RoutineWithStatus(routine) for routine in during_work_routines]
        self._outside_work_rs = [RoutineWithStatus(routine) for routine in outside_work_routines]

        super().__init__(age=age,
                         home=home,
                         registry=registry,
                         name=name,
                         risk=risk,
                         night_hours=night_hours,
                         regulation_compliance_prob=regulation_compliance_prob,
                         init_state=init_state,
                         numpy_rng=numpy_rng)

    @property
    def work(self) -> LocationID:
        return self._work

    @property
    def assigned_locations(self) -> Sequence[LocationID]:
        return self._home, self._work

    @property
    def at_work(self) -> bool:
        """Return True if the person is at work and False otherwise"""
        return self._state.current_location == self.work

    def _sync(self, sim_time: SimTime) -> None:
        super()._sync(sim_time)

        for rws in self._during_work_rs + self._outside_work_rs:
            rws.sync(sim_time)

        if sim_time.week_day == 0:
            self._socializing_done = False

    def step(self, sim_time: SimTime, contact_tracer: Optional[ContactTracer] = None) -> Optional[NoOP]:
        step_ret = super().step(sim_time, contact_tracer)
        if step_ret != NOOP:
            return step_ret

        if sim_time in self._work_time:
            # execute during work time routines
            ret = execute_routines(person=self, routines_with_status=self._during_work_rs, numpy_rng=self._numpy_rng)
            if ret != NOOP:
                return ret

            # no more routines to execute, go back to office
            if not self.at_work and self._numpy_rng.uniform() < self._to_work_at_hour_prob:
                if self.enter_location(self.work):
                    return None
        else:
            # execute outside work time routines
            ret = execute_routines(person=self, routines_with_status=self._outside_work_rs, numpy_rng=self._numpy_rng)
            if ret != NOOP:
                return ret

            # if not at home go home
            if not self.at_home and self._numpy_rng.uniform() < self._to_home_hour_prob:
                self.enter_location(self.home)
                return None

        return NOOP
