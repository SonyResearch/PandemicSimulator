"""This script tunes the simulator's hyperparameters by utilizing Bayesian Optimization,
and measures a hyperparameter set's fitness according to Sweden's death data with the
simulator output's time to peak and the difference over the rise of the curve. The
hyperparameters that are tuned in the script include spread rate and social distancing
rate
"""
import dataclasses
from dataclasses import dataclass
from typing import cast

import GPyOpt
import matplotlib.pyplot as plt
import numpy as np
from pandas import read_csv
from pandemic_simulator.environment import PandemicSimOpts, PandemicSimNonCLIOpts, \
    InfectionSummary, Hospital, HospitalState, swedish_regulations
from pandemic_simulator.script_helpers import make_sim, population_params
from tqdm import trange

SEED = 30
MAX_EVAL_TRIALS_TO_VALID = 5

np.random.seed(SEED)


@dataclass
class EvalResult:
    deaths: np.ndarray
    hospitalizations: np.ndarray

    def is_valid(self) -> bool:
        return bool(np.sum(self.deaths) > 0)


def eval_params(params: np.ndarray,
                max_episode_length: int,
                trial_cnt: int = 0) -> EvalResult:
    """Evaluate the params and return the result

    :param params: spread rate and social distancing rate
    :param max_episode_length: length of simulation run in days
    :param trial_cnt: evaluation trial count
    :returns: EvalResult instance
    """
    if trial_cnt >= MAX_EVAL_TRIALS_TO_VALID:
        raise Exception(f'Could not find a valid evaluation for the params: {params} within the specified number'
                        f'of trials: {MAX_EVAL_TRIALS_TO_VALID}.')

    spread_rate = params[:, 0][0]
    social_distancing = params[:, 1][0]
    deaths = []
    hospitalizations = []
    seed = SEED + trial_cnt

    if trial_cnt == 0:
        print(f'Running with spread rate: {spread_rate} and social distancing: {social_distancing}')
    else:
        print(f'Re-Running with a different seed: {seed}')

    numpy_rng = np.random.RandomState(seed=seed)
    sim_non_cli_opts = PandemicSimNonCLIOpts(population_params.above_medium_town_population_params)
    sim_opts = PandemicSimOpts(infection_spread_rate_mean=spread_rate)
    sim = make_sim(sim_opts, sim_non_cli_opts, numpy_rng=numpy_rng)

    # using swedish stage 1 regulation with the given social distancing to calibrate
    covid_regulation = dataclasses.replace(swedish_regulations[1], social_distancing=social_distancing)
    sim.execute_regulation(regulation=covid_regulation)

    hospital_ids = sim.registry.location_ids_of_type(Hospital)

    hospital_weekly=0
    for i in trange(max_episode_length, desc='Simulating day'):
        sim.step_day()
        state = sim.state
        num_deaths = state.global_infection_summary[InfectionSummary.DEAD]
        deaths.append(num_deaths)
        num_hospitalizations = sum([cast(HospitalState, state.id_to_location_state[loc_id]).num_admitted_patients
                                    for loc_id in hospital_ids])
        hospital_weekly += num_hospitalizations
        if i % 7 is 0:
            hospitalizations.append(hospital_weekly)
            hospital_weekly = 0
        # hospitalizations.append(num_hospitalizations)
    eval_result = EvalResult(deaths=np.asarray(deaths), hospitalizations=np.asarray(hospitalizations))

    return eval_result if eval_result.is_valid() else eval_params(params, max_episode_length, trial_cnt=trial_cnt + 1)


def real_world_data() -> EvalResult:
    """Extract and treat real-world data from WHO

    :returns: real-world death data
    """
    # using Sweden's death data
    deaths_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/new_deaths.csv'
    deaths_df = read_csv(deaths_url, header=0)
    real_deaths = deaths_df['Sweden'].values
    real_deaths = real_deaths[~np.isnan(real_deaths)]

    real_hosp = [0, 0, 0, 0, 3, 16, 87, 235, 274, 285, 247, 235, 186, 154, 122, 110, 120, 121, 90, 73, 55, 34, 14, 14, 12, 11, 16, 13, 8, 7, 8, 8, 7]

    return EvalResult(deaths=real_deaths, hospitalizations=np.asarray(real_hosp))


def least_diff(world_data: np.ndarray, sim_data: np.ndarray) -> float:
    """Calculate sum difference over the rises of the two curves

    :param world_data: normalized deaths-per-day real-world data
    :param sim_data: normalized deaths-per-day simulator data
    :returns: the sum of differences between the rises of the two curves
    """
    score = 0
    for j in range(min(len(world_data), len(sim_data))):
        score += abs(world_data[j] - sim_data[j])
    return score


def obj_func(params: np.ndarray) -> float:
    """Objective function calculates fitness score for a given parameter set

    :param params: spread rate and social distancing rate to be evaluated
    :returns: fitness score of parameter set
    """
    # get real world data
    real_data = real_world_data().hospitalizations

    # get sim data and extract deaths per day
    eval_result: EvalResult = eval_params(params, 180)
    sim_data = eval_result.hospitalizations

    # sim_data = sim_output[1:] - sim_output[:-1]

    # start data at first death
    real_data = np.trim_zeros(real_data, 'f')
    sim_data = np.trim_zeros(sim_data, 'f')

    # calculate sliding average
    real_data = np.convolve(real_data, np.ones(5) / 5, mode='same')
    sim_data = np.convolve(sim_data, np.ones(5) / 5, mode='same')

    # calculate peak score
    real_peak = np.argmax(real_data).item()
    sim_peak = np.argmax(sim_data).item()
    peak_score = abs(sim_peak - real_peak)

    # normalize
    real_data /= real_data[real_peak]
    sim_data /= sim_data[sim_peak]

    # calculate least difference over rise of curve
    rise_score = least_diff(world_data=real_data, sim_data=sim_data)

    print('score: ', rise_score + peak_score)
    return float(rise_score + peak_score)


def make_plots(params: np.ndarray) -> None:
    """Plot final parameter set output against real world data

    :param params: resulting spread rate and social distancing rate
    """
    # get real world data and calibrated simulator output
    real_data = real_world_data().hospitalizations

    eval_result: EvalResult = eval_params(params, 200)
    sim_data = eval_result.hospitalizations

    # sim_data = sim_output[1:] - sim_output[:-1]

    # treat data
    real_data = np.trim_zeros(real_data, 'f')
    sim_data = np.trim_zeros(sim_data, 'f')
    real_data = np.convolve(real_data, np.ones(5) / 5, mode='same')
    sim_data = np.convolve(sim_data, np.ones(5) / 5, mode='same')
    real_data /= real_data[np.argmax(real_data).item()]
    sim_data /= sim_data[np.argmax(sim_data).item()]

    # plot calibrated simulator run against real-world data
    length = min(len(real_data), len(sim_data))
    plt.plot(np.linspace(start=0, stop=length, num=length), sim_data[:length])
    plt.plot(np.linspace(start=0, stop=length, num=length), real_data[:length])
    plt.legend(["PANDEMICSIM", "Sweden"])
    plt.xlabel("Days Passed")
    plt.ylabel("Deaths Per Day (normalized)")
    plt.show()


if __name__ == '__main__':
    bounds2d = [{'name': 'spread rate', 'type': 'continuous', 'domain': (0.005, 0.03)},
                {'name': 'contact rate', 'type': 'continuous', 'domain': (0., 0.8)}]
    maxiter = 20
    myBopt_2d = GPyOpt.methods.BayesianOptimization(obj_func, domain=bounds2d)
    myBopt_2d.run_optimization(max_iter=maxiter)

    print("=" * 20)
    print("Value of (spread rate, contact rate) that minimises the objective:" + str(myBopt_2d.x_opt))
    print("Minimum value of the objective: " + str(myBopt_2d.fx_opt))
    print("=" * 20)

    make_plots(np.array([[myBopt_2d.x_opt[0], myBopt_2d.x_opt[1]]], dtype=np.float64))

    myBopt_2d.plot_acquisition()
