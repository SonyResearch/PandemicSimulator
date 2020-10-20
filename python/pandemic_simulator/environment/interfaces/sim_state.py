# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from dataclasses import dataclass
from typing import Dict

from .pandemic_testing import GlobalTestingState
from .ids import LocationID, PersonID
from .infection_model import InfectionSummary
from .location_states import LocationState
from .person import PersonState
from .sim_time import SimTime

__all__ = ['PandemicSimState']


@dataclass
class PandemicSimState:
    id_to_person_state: Dict[PersonID, PersonState]
    id_to_location_state: Dict[LocationID, LocationState]
    global_infection_summary: Dict[InfectionSummary, int]
    global_testing_state: GlobalTestingState
    infection_above_threshold: bool
    regulation_stage: int
    sim_time: SimTime
