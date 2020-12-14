# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import Optional, Sequence

import numpy as np

from .base import BasePerson
from .routine_utils import RoutineWithStatus, execute_routines
from ..interfaces import LocationID, SimTime, NoOP, NOOP, Registry, PersonState, PersonRoutine, ContactTracer, PersonID

__all__ = ['Retired']


class Retired(BasePerson):
    """Class that implements a retired person"""

    _routines_with_status: Sequence[RoutineWithStatus]

    def __init__(self,
                 person_id: PersonID,
                 home: LocationID,
                 registry: Registry,
                 routines: Sequence[PersonRoutine] = (),
                 regulation_compliance_prob: float = 1.0,
                 init_state: Optional[PersonState] = None,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param person_id: PersonID instance
        :param home: Home location id
        :param registry: Registry instance to register the person and handle peron's entry to a location
        :param routines: A sequence of person routines to run
        :param regulation_compliance_prob: probability of complying to a regulation
        :param init_state: Optional initial state of the person
        :param numpy_rng: Random number generator
        """
        self._routines_with_status = [RoutineWithStatus(routine) for routine in routines]

        super().__init__(person_id=person_id,
                         home=home,
                         registry=registry,
                         regulation_compliance_prob=regulation_compliance_prob,
                         init_state=init_state,
                         numpy_rng=numpy_rng)

    def _sync(self, sim_time: SimTime) -> None:
        super()._sync(sim_time)

        for rws in self._routines_with_status:
            rws.sync(sim_time)

    def step(self, sim_time: SimTime, contact_tracer: Optional[ContactTracer] = None) -> Optional[NoOP]:
        step_ret = super().step(sim_time, contact_tracer)
        if step_ret != NOOP:
            return step_ret

        # execute routines
        ret = execute_routines(person=self, routines_with_status=self._routines_with_status, numpy_rng=self._numpy_rng)
        if ret != NOOP:
            return ret

        # if not at home go home
        if not self.at_home:
            self.enter_location(self.home)
            return None

        return NOOP

    def reset(self) -> None:
        super().reset()
        for rws in self._routines_with_status:
            rws.reset()
