# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from dataclasses import dataclass
from typing import Sequence, Type, cast, Optional

import numpy as np

from .ids import LocationID
from .infection_model import InfectionSummary, sorted_infection_summary
from .location_states import NonEssentialBusinessLocationState
from .sim_state import PandemicSimState

__all__ = ['PandemicObservation','PanObsOptional']


@dataclass
class PandemicObservation:
    """Dataclass that updates numpy arrays with information from PandemicSimState. Typically, this observation is
    used by the reinforcement learning interface."""

    global_infection_summary: np.ndarray
    global_testing_summary: np.ndarray
    stage: np.ndarray
    infection_above_threshold: np.ndarray
    time_day: np.ndarray
    unlocked_non_essential_business_locations: Optional[np.ndarray] = None

    @classmethod
    def create_empty(cls: Type['PandemicObservation'],
                     history_size: int = 1,
                     num_non_essential_business: Optional[int] = None) -> 'PandemicObservation':
        """
        Creates an empty observation TNC layout array.

        :param history_size: Size of history. If set > 1, the observation can hold information from multiple sequences
            of PandemicSimStates.
        :param num_non_essential_business: Number of non essential business locations.
        :return: an empty PandemicObservation instance
        """
        return PandemicObservation(global_infection_summary=np.zeros((history_size, 1, len(InfectionSummary))),
                                   global_testing_summary=np.zeros((history_size, 1, len(InfectionSummary))),
                                   stage=np.zeros((history_size, 1, 1)),
                                   infection_above_threshold=np.zeros((history_size, 1, 1)),
                                   time_day=np.zeros((history_size, 1, 1)),
                                   unlocked_non_essential_business_locations=np.zeros((history_size, 1,
                                                                                       num_non_essential_business))
                                   if num_non_essential_business is not None else None)

    def update_obs_with_sim_state(self, sim_state: PandemicSimState,
                                  hist_index: int = 0,
                                  business_location_ids: Optional[Sequence[LocationID]] = None) -> None:
        """
        Update the PandemicObservation with the information from PandemicSimState.

        :param sim_state: PandemicSimState instance
        :param hist_index: history time index
        :param business_location_ids: business location ids
        """
        assert hist_index < self.global_infection_summary.shape[0]
        if self.unlocked_non_essential_business_locations is not None and business_location_ids is not None:
            unlocked_non_essential_business_locations = np.asarray([int(not cast(NonEssentialBusinessLocationState,
                                                                                 sim_state.id_to_location_state[
                                                                                     loc_id]).locked)
                                                                    for loc_id in business_location_ids])
            self.unlocked_non_essential_business_locations[hist_index, 0] = unlocked_non_essential_business_locations

        gis = np.asarray([sim_state.global_infection_summary[k] for k in sorted_infection_summary])[None, None, ...]
        self.global_infection_summary[hist_index, 0] = gis

        gts = np.asarray([sim_state.global_testing_state.summary[k] for k in sorted_infection_summary])[None, None, ...]
        self.global_testing_summary[hist_index, 0] = gts

        self.stage[hist_index, 0] = sim_state.regulation_stage

        self.infection_above_threshold[hist_index, 0] = int(sim_state.infection_above_threshold)

        self.time_day[hist_index, 0] = int(sim_state.sim_time.day)

    @property
    def infection_summary_labels(self) -> Sequence[str]:
        """Return the label for each index in global_infection(or testing)_summary observation entry"""
        return [k.value for k in sorted_infection_summary]

@dataclass
class PanObsOptional(PandemicObservation):

    use_gis: bool = False
    use_gts: bool = True
    use_stage: bool = True
    use_infection_above_threshold: bool = False
    #if crit flag accepted add it here
    use_time_day: bool = False
    use_unlocked_non_essential_business_locations: bool = False

    @classmethod
    def create_empty(cls: Type['PanObsOptional'],
                     history_size: int = 1,
                     num_non_essential_business: Optional[int] = None,
                     use_gis: bool = False,
                     use_gts: bool = True,
                     use_stage: bool = True,
                     use_infection_above_threshold: bool  = False,
                     #if crit flag accepted add it here
                     use_time_day: bool = False,
                     use_unlocked_non_essential_business_locations: bool = False) -> 'PanObsOptional':

                     return PanObsOptional(global_infection_summary=np.zeros((history_size, 1, len(InfectionSummary))) if use_gis else None,
                                   global_testing_summary=np.zeros((history_size, 1, len(InfectionSummary)))if use_gts else None,
                                   stage=np.zeros((history_size, 1, 1))if use_stage else None,
                                   infection_above_threshold=np.zeros((history_size, 1, 1))if use_infection_above_threshold else None,
                                   time_day=np.zeros((history_size, 1, 1))if use_time_day else None,
                                   unlocked_non_essential_business_locations=np.zeros((history_size, 1,
                                                                                       num_non_essential_business))
                                   if use_unlocked_non_essential_business_locations else None)

    def update_obs_with_sim_state(self, sim_state: PandemicSimState,
                                  hist_index: int = 0,
                                  business_location_ids: Optional[Sequence[LocationID]] = None) -> None:
        """
        Update the PandemicObservation with the information from PandemicSimState.

        :param sim_state: PandemicSimState instance
        :param hist_index: history time index
        :param business_location_ids: business location ids
        """
        if self.use_unlocked_non_essential_business_locations:
            if self.unlocked_non_essential_business_locations is not None and business_location_ids is not None:
                unlocked_non_essential_business_locations = np.asarray([int(not cast(NonEssentialBusinessLocationState,
                                                                                    sim_state.id_to_location_state[
                                                                                        loc_id]).locked)
                                                                        for loc_id in business_location_ids])
                self.unlocked_non_essential_business_locations[hist_index, 0] = unlocked_non_essential_business_locations

        if self.use_gis:
            gis = np.asarray([sim_state.global_infection_summary[k] for k in sorted_infection_summary])[None, None, ...]
            self.global_infection_summary[hist_index, 0] = gis

        if self.use_gts:
            gts = np.asarray([sim_state.global_testing_state.summary[k] for k in sorted_infection_summary])[None, None, ...]
            self.global_testing_summary[hist_index, 0] = gts

        if self.use_stage:
            self.stage[hist_index, 0] = sim_state.regulation_stage

        if self.use_infection_above_threshold:
            self.infection_above_threshold[hist_index, 0] = int(sim_state.infection_above_threshold)

        if self.use_time_day:
            self.time_day[hist_index, 0] = int(sim_state.sim_time.day)
                     
