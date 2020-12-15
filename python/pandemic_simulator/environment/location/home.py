# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from dataclasses import dataclass

from .base import BaseLocation
from ..interfaces import LocationState, ContactRate, SimTime, SimTimeTuple, LocationRule

__all__ = ['Home', 'HomeState']


@dataclass
class HomeState(LocationState):
    contact_rate: ContactRate = ContactRate(0, 1, 0, 0.5, 0.3, 0.3)


class Home(BaseLocation[HomeState]):
    """Class that implements a standard Home location. """

    @property
    def state_type(self) -> Type[CemeteryState]:

    def create_state(self) -> HomeState:
        social_event_time = SimTimeTuple(hours=tuple(range(15, 20)),
                                         days=tuple(self._numpy_rng.randint(0, 365, 12)))
        return HomeState(visitor_time=social_event_time)

    def sync(self, sim_time: SimTime) -> None:
        super().sync(sim_time)
        self._state.social_gathering_event = sim_time in self._state.visitor_time

    def update_rules(self, new_rule: LocationRule) -> None:
        pass
