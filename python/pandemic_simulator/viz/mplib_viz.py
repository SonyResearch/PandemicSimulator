# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
import string
from typing import List, Any

import numpy as np
from cycler import cycler
from matplotlib import pyplot as plt

from .mplab_evaluation import inf_colors
from .pandemic_viz import PandemicViz
from ..environment import PandemicObservation, sorted_infection_summary, InfectionSummary, LocationParams, \
    PandemicSimState
from ..utils import checked_cast

__all__ = ['MatplotLibViz']


class MatplotLibViz(PandemicViz):
    """Pandemic19 reinforcement learning matplotlib visualization"""

    _num_persons: int
    _max_hospitals_capacity: int
    _num_stages: int
    _show_reward: bool
    _show_stages: bool

    _gis: List[np.ndarray]
    _gts: List[np.ndarray]
    _los: List[np.ndarray]
    _stages: List[np.ndarray]
    _rewards: List[float]

    _gis_legend: List[str]
    _los_legend: List[str]
    _critical_index: int
    _stage_indices: np.ndarray

    def __init__(self, num_persons: int,
                 hospital_params: LocationParams,
                 num_stages: int,
                 show_reward: bool = False,
                 show_stages: bool = True):
        """
        :param num_persons: total number of persons in the simulator
        :param hospital_params: hospital location params
        :param num_stages: number of stages in the environment
        :param show_reward: show cumulative reward plot
        :param show_stages: show stages plot
        """
        self._num_persons = num_persons
        self._max_hospitals_capacity = hospital_params.num * hospital_params.visitor_capacity
        self._num_stages = num_stages
        self._show_reward = show_reward
        self._show_stages = show_stages

        self._gis = []
        self._gts = []
        self._los = []
        self._stages = []
        self._rewards = []

        self._gis_legend = []
        self._critical_index = 0
        self._stage_indices = np.arange(num_stages)[..., None]

    def record(self, data: Any, **kwargs: Any) -> None:
        if isinstance(data, PandemicSimState):
            state = checked_cast(PandemicSimState, data)
            obs = PandemicObservation.create_empty(len(state.location_occupancy_summary))
            obs.update_obs_with_sim_state(state)
        elif isinstance(data, PandemicObservation):
            obs = data
        else:
            raise ValueError('Unsupported data type')

        if len(self._gis_legend) == 0:
            self._gis_legend = list(obs.infection_summary_labels)
            self._los_legend = list(obs.location_occupancy_labels)
            self._critical_index = self._gis_legend.index(InfectionSummary.CRITICAL.value)

        self._gis.append(obs.global_infection_summary)
        self._gts.append(obs.global_testing_summary)
        self._los.append(obs.location_occupancy_summary)
        self._stages.append(obs.stage)
        if 'reward' in kwargs:
            self._rewards.append(kwargs['reward'])

    def plot(self) -> None:
        """Make plots"""
        gis = np.vstack(self._gis).squeeze()
        gts = np.vstack(self._gts).squeeze()
        los = np.mean(self._los, axis=0).squeeze()
        los = 100 * los / los.sum()
        stages = np.concatenate(self._stages).squeeze()

        ncols = 4
        nrows = int(np.ceil((4 + self._show_reward + self._show_stages) / 4))

        plt.figure(figsize=(4 * ncols, 4 * nrows))
        plt.rc('axes', prop_cycle=cycler(color=inf_colors))

        axs = list()
        ax_i = 0

        ax_i += 1
        axs.append(plt.subplot(nrows, ncols, ax_i))
        plt.plot(gis)
        plt.legend(self._gis_legend, loc=1)
        plt.ylim([-0.1, self._num_persons + 1])
        plt.title('Global Infection Summary')
        plt.xlabel('time (days)')
        plt.ylabel('persons')

        ax_i += 1
        axs.append(plt.subplot(nrows, ncols, ax_i))
        plt.plot(gts)
        plt.legend(self._gis_legend, loc=1)
        plt.ylim([-0.1, self._num_persons + 1])
        plt.title('Global Testing Summary')
        plt.xlabel('time (days)')
        plt.ylabel('persons')

        ax_i += 1
        axs.append(plt.subplot(nrows, ncols, ax_i))
        plt.plot(gis[:, self._critical_index])
        plt.plot(np.arange(gis.shape[0]), np.ones(gis.shape[0]) * self._max_hospitals_capacity, 'y')
        plt.legend([InfectionSummary.CRITICAL.value, 'Max hospital capacity'], loc=1)
        plt.ylim([-0.1, self._max_hospitals_capacity * 3])
        plt.title('Critical Summary')
        plt.xlabel('time (days)')
        plt.ylabel('persons')

        ax_i += 1
        axs.append(plt.subplot(nrows, ncols, ax_i))
        x = np.arange(len(los))
        plt.bar(x, los, color='#009ACD')
        plt.xticks(x, self._los_legend, rotation=45, fontsize=8)
        plt.title('Location Occupancy Summary')
        plt.ylabel('occupancy (%)')
        plt.ylim([0, None])

        if self._show_stages:
            ax_i += 1
            axs.append(plt.subplot(nrows, ncols, ax_i))
            plt.plot(stages)
            plt.ylim([-0.1, self._num_stages + 1])
            plt.title('Stage')
            plt.xlabel('time (days)')

        if self._show_reward and len(self._rewards) > 0:
            ax_i += 1
            axs.append(plt.subplot(nrows, ncols, ax_i))
            plt.plot(np.cumsum(self._rewards))
            plt.title('Cumulative Reward')
            plt.xlabel('time (days)')

        plot_ref_labels = string.ascii_lowercase
        plot_ref_label_i = 0
        for ax in axs:
            ax.annotate(f'({plot_ref_labels[plot_ref_label_i]})', (0.5, 0.), xytext=(0, -25 - 20),
                        textcoords='offset points', xycoords='axes fraction',
                        ha='center', va='center', size=14)
            plot_ref_label_i += 1

        plt.tight_layout()

        plt.show()
