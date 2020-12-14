# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from typing import Optional, Sequence, List

import numpy as np

from .base import BasePerson
from .routine_utils import RoutineWithStatus, execute_routines
from ..interfaces import PersonState, LocationID, Registry, SimTime, NoOP, SimTimeTuple, NOOP, PersonRoutine, \
    ContactTracer, PersonID

__all__ = ['Worker']


class Worker(BasePerson):
    """Class that implements a basic worker."""

    _work: LocationID
    _work_time: SimTimeTuple
    _during_work_rs: List[RoutineWithStatus]
    _outside_work_rs: List[RoutineWithStatus]

    def __init__(self,
                 person_id: PersonID,
                 home: LocationID,
                 work: LocationID,
                 registry: Registry,
                 work_time: Optional[SimTimeTuple] = None,
                 during_work_routines: Sequence[PersonRoutine] = (),
                 outside_work_routines: Sequence[PersonRoutine] = (),
                 regulation_compliance_prob: float = 1.0,
                 init_state: Optional[PersonState] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param person_id: PersonID instance
        :param home: Home location id
        :param work: Work location id
        :param registry: Registry instance to register the person and handle peron's entry to a location
        :param work_time: Work time specified in SimTimeTuples. Default - 9am-5pm and Mon-Fri
        :param during_work_routines: A sequence of person routines to run during work time
        :param outside_work_routines: A sequence of person routines to run outside work time
        :param regulation_compliance_prob: probability of complying to a regulation
        :param init_state: Optional initial state of the person
        :param numpy_rng: Random number generator
        """
        assert person_id.age >= 18, "Workers's age must be >= 18"
        self._work = work
        self._work_time = work_time or SimTimeTuple(hours=tuple(range(9, 18)), week_days=tuple(range(0, 5)))
        self._during_work_rs = [RoutineWithStatus(routine) for routine in during_work_routines]
        self._outside_work_rs = [RoutineWithStatus(routine) for routine in outside_work_routines]

        super().__init__(person_id=person_id,
                         home=home,
                         registry=registry,
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

    def step(self, sim_time: SimTime, contact_tracer: Optional[ContactTracer] = None) -> Optional[NoOP]:
        step_ret = super().step(sim_time, contact_tracer)
        if step_ret != NOOP:
            return step_ret

        if sim_time in self._work_time:
            # execute during work routines
            ret = execute_routines(person=self, routines_with_status=self._during_work_rs, numpy_rng=self._numpy_rng)
            if ret != NOOP:
                return ret

            # no more routines to execute, go back to office
            if not self.at_work and self.enter_location(self.work):
                return None
        else:
            # execute outside work time routines
            ret = execute_routines(person=self, routines_with_status=self._outside_work_rs, numpy_rng=self._numpy_rng)
            if ret != NOOP:
                return ret

            # no more routines to execute, go home
            if not self.at_home:
                self.enter_location(self.home)
                return None

        return NOOP

    def reset(self) -> None:
        super().reset()
        for rws in self._during_work_rs + self._outside_work_rs:
            rws.reset()
