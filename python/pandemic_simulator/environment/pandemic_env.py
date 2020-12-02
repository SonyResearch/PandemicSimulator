# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from typing import List, Optional, Dict, Tuple

import gym

from .done import DoneFunction
from .interfaces import LocationID, PandemicObservation, NonEssentialBusinessLocationState, PandemicRegulation
from .pandemic_sim import PandemicSim
from .regulation_stages import DEFAULT_REGULATION, austin_regulations
from .reward import RewardFunction

__all__ = ['PandemicGymEnv']


class PandemicGymEnv(gym.Env):
    """A gym environment interface wrapper for the Pandemic Simulator."""

    _pandemic_sim: PandemicSim
    _obs_history_size: int
    _sim_steps_per_regulation: int
    _non_essential_business_loc_ids: Optional[List[LocationID]]
    _reward_fn: Optional[RewardFunction]
    _done_fn: Optional[DoneFunction]

    _last_observation: PandemicObservation
    _last_reward: float

    def __init__(self,
                 pandemic_sim: PandemicSim,
                 stage_to_regulation: Optional[Dict[int, PandemicRegulation]] = None,
                 obs_history_size: int = 1,
                 sim_steps_per_regulation: int = 24,
                 non_essential_business_location_ids: Optional[List[LocationID]] = None,
                 reward_fn: Optional[RewardFunction] = None,
                 done_fn: Optional[DoneFunction] = None):
        """
        :param pandemic_sim: Pandemic simulator instance
        :param stage_to_regulation: A mapping of an integer stage action to a pandemic regulation. If None, a default
            5 stages mapping is used.
        :param obs_history_size: number of latest sim step states to include in the observation
        :param sim_steps_per_regulation: number of sim_steps to run for each regulation
        :param non_essential_business_location_ids: an ordered list of non-essential business location ids
        :param reward_fn: reward function
        :param done_fn: done function
        """
        self._pandemic_sim = pandemic_sim
        self._stage_to_regulation = (stage_to_regulation if stage_to_regulation is not None
                                     else {reg.stage: reg for reg in austin_regulations})
        self._obs_history_size = obs_history_size
        self._sim_steps_per_regulation = sim_steps_per_regulation

        if non_essential_business_location_ids is not None:
            for loc_id in non_essential_business_location_ids:
                assert isinstance(self._pandemic_sim.state.id_to_location_state[loc_id],
                                  NonEssentialBusinessLocationState)
        self._non_essential_business_loc_ids = non_essential_business_location_ids

        self._reward_fn = reward_fn
        self._done_fn = done_fn

        self.action_space = gym.spaces.Discrete(len(self._stage_to_regulation))

    @property
    def observation(self) -> PandemicObservation:
        return self._last_observation

    @property
    def last_reward(self) -> float:
        return self._last_reward

    def step(self, action: int) -> Tuple[PandemicObservation, float, bool, Dict]:
        assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))

        # get the regulation
        if action == 0 and action != self._last_observation.stage:
            regulation = DEFAULT_REGULATION
        else:
            regulation = self._stage_to_regulation[action]

        # execute the given regulation
        self._pandemic_sim.execute_regulation(regulation=regulation)

        # update the sim until next regulation interval trigger and construct obs from state hist
        obs = PandemicObservation.create_empty(history_size=self._obs_history_size,
                                               num_non_essential_business=len(self._non_essential_business_loc_ids)
                                               if self._non_essential_business_loc_ids is not None else None)
        hist_index = 0
        for i in range(self._sim_steps_per_regulation):
            # step sim
            self._pandemic_sim.step()

            # store only the last self._history_size state values
            if i >= (self._sim_steps_per_regulation - self._obs_history_size):
                obs.update_obs_with_sim_state(self._pandemic_sim.state, hist_index,
                                              self._non_essential_business_loc_ids)
                hist_index += 1

        prev_obs = self._last_observation
        self._last_reward = self._reward_fn.calculate_reward(prev_obs, action, obs) if self._reward_fn else 0.
        done = self._done_fn.calculate_done(obs, action) if self._done_fn else False
        self._last_observation = obs

        return self._last_observation, self._last_reward, done, {}

    def reset(self) -> PandemicObservation:
        self._pandemic_sim.reset()
        self._last_observation = PandemicObservation.create_empty(
            history_size=self._obs_history_size,
            num_non_essential_business=len(self._non_essential_business_loc_ids)
            if self._non_essential_business_loc_ids is not None else None)
        self._last_reward = 0.0
        if self._done_fn is not None:
            self._done_fn.reset()
        return self._last_observation

    def render(self, mode: str = 'human') -> bool:
        pass
