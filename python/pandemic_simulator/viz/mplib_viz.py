# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
import string
from typing import List, Any, Dict

import numpy as np
from cycler import cycler
from matplotlib import pyplot as plt

from .mplab_evaluation import inf_colors
from .pandemic_viz import PandemicViz
from ..environment import PandemicObservation, InfectionSummary, LocationParams, \
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
    _loc_assignee_visits: List[np.ndarray]
    _loc_visitor_visits: List[np.ndarray]
    _location_type_to_is: Dict[str, int]
    _stages: List[np.ndarray]
    _rewards: List[float]

    _gis_legend: List[str]
    _loc_types: List[str]
    _person_types: List[str]
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
        self._loc_assignee_visits = []
        self._loc_visitor_visits = []
        self._location_type_to_is = {}
        self._stages = []
        self._rewards = []

        self._gis_legend = []
        self._loc_types = []
        self._person_types = []
        self._critical_index = 0
        self._stage_indices = np.arange(num_stages)[..., None]

    def record(self, data: Any, **kwargs: Any) -> None:
        if isinstance(data, PandemicSimState):
            state = checked_cast(PandemicSimState, data)
            obs = PandemicObservation.create_empty()
            obs.update_obs_with_sim_state(state)
            if len(self._loc_types) == 0:
                self._loc_types = sorted(set(k[0] for k in state.global_location_summary.keys()))
                self._person_types = sorted(set(k[1] for k in state.global_location_summary.keys()))

            _av = np.zeros((1, len(self._loc_types), len(self._person_types)))
            _vv = np.zeros((1, len(self._loc_types), len(self._person_types)))
            for i in range(len(self._loc_types)):
                for j in range(len(self._person_types)):
                    ec = state.global_location_summary[(self._loc_types[i], self._person_types[j])].entry_count
                    vc = state.global_location_summary[(self._loc_types[i], self._person_types[j])].visitor_count
                    _av[0, i, j] = ec - vc
                    _vv[0, i, j] = vc
            self._loc_assignee_visits.append(_av)
            self._loc_visitor_visits.append(_vv)
            self._location_type_to_is = {k.__name__: v for k, v in state.location_type_infection_summary.items()}

        elif isinstance(data, PandemicObservation):
            obs = data
        else:
            raise ValueError('Unsupported data type')

        if len(self._gis_legend) == 0:
            self._gis_legend = list(obs.infection_summary_labels)
            self._critical_index = self._gis_legend.index(InfectionSummary.CRITICAL.value)

        self._gis.append(obs.global_infection_summary)
        self._gts.append(obs.global_testing_summary)
        self._stages.append(obs.stage)
        if 'reward' in kwargs:
            self._rewards.append(kwargs['reward'])

    def plot(self) -> None:
        """Make plots"""
        gis = np.vstack(self._gis).squeeze()
        gts = np.vstack(self._gts).squeeze()
        stages = np.concatenate(self._stages).squeeze()

        ncols = 3
        nrows = int(np.ceil((3 + 2 * int(len(self._loc_assignee_visits) > 0) +
                             int(len(self._location_type_to_is) > 0) +
                             self._show_reward + self._show_stages) / ncols))

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

        loc_types = self._loc_types
        if len(self._loc_assignee_visits) > 0:
            ax_i += 1
            axs.append(plt.subplot(nrows, ncols, ax_i))
            lv = self._loc_assignee_visits[-1].squeeze()
            indices = np.argsort(lv.sum(axis=1), axis=0)[::-1]
            lv = lv[indices]
            loc_types = [self._loc_types[i] for i in indices]
            x = np.arange(lv.shape[0])
            p = []
            colors = ['g', 'r', 'b']
            bottom = np.zeros(lv.shape[0])
            for j in range(lv.shape[1] - 1, -1, -1):
                p.append(plt.bar(x, lv[:, j], color=colors[j], alpha=0.5, bottom=bottom))
                bottom += lv[:, j]
            plt.xticks(x, loc_types, rotation=60, fontsize=8)
            plt.title(f'Location Assignee Visits\n(in {len(self._loc_assignee_visits)} days)')
            plt.ylabel('num_visits / num_persons')
            plt.ylim([0, None])
            plt.legend(p, self._person_types[::-1])

            ax_i += 1
            axs.append(plt.subplot(nrows, ncols, ax_i))
            lv = self._loc_visitor_visits[-1].squeeze()
            lv = lv[indices]
            loc_types = [self._loc_types[i] for i in indices]
            p = []
            bottom = np.zeros(lv.shape[0])
            for j in range(lv.shape[1] - 1, -1, -1):
                p.append(plt.bar(x, lv[:, j], color=colors[j], alpha=0.5, bottom=bottom))
                bottom += lv[:, j]
            plt.xticks(x, loc_types, rotation=60, fontsize=8)
            plt.title(f'Location Visitor Visits\n(in {len(self._loc_visitor_visits)} days)')
            plt.ylabel('num_visits / num_persons')
            plt.ylim([0, None])
            plt.legend(p, self._person_types[::-1])

        if len(self._location_type_to_is) > 0:
            ax_i += 1
            axs.append(plt.subplot(nrows, ncols, ax_i))
            x = np.arange(len(loc_types))
            plt.bar(x, [self._location_type_to_is[k] / self._num_persons for k in loc_types], color='r', alpha=0.5)
            plt.xticks(x, loc_types, rotation=60, fontsize=8)
            plt.ylim([0, None])
            plt.title('% Infections / Location Type')
            plt.ylabel('% infections')

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
