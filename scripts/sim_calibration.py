"""This script tunes the simulator's hyperparameters by utilizing Bayesian Optimization,
and measures a hyperparameter set's fitness according to Sweden's death data with the
simulator output's time to peak and the difference over the rise of the curve. The
hyperparameters that are tuned in the script include spread rate and social distancing
rate
"""
import dataclasses
from dataclasses import dataclass
from typing import cast, Optional

import GPyOpt
import matplotlib.pyplot as plt
import numpy as np
from pandas import read_csv
from tqdm import trange

from pandemic_simulator.environment import PandemicSimOpts, PandemicSimNonCLIOpts, \
    InfectionSummary, Hospital, HospitalState, swedish_regulations
from pandemic_simulator.script_helpers import make_sim, population_params

SEED = 30
MAX_EVAL_TRIALS_TO_VALID = 5

np.random.seed(SEED)


@dataclass
class CalibrationData:
    deaths: np.ndarray
    hospitalizations: np.ndarray

    def is_valid(self) -> bool:
        return bool(np.sum(self.deaths) > 0)


def eval_params(params: np.ndarray,
                max_episode_length: int,
                trial_cnt: int = 0) -> CalibrationData:
    """Evaluate the params and return the result

    :param params: spread rate and social distancing rate
    :param max_episode_length: length of simulation run in days
    :param trial_cnt: evaluation trial count
    :returns: CalibrationData instance
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
    sim_non_cli_opts = PandemicSimNonCLIOpts(population_params.small_town_population_params)
    # Set visitor (patient) capacity to a high number for calibration.
    sim_non_cli_opts.population_params.location_type_to_params[Hospital].visitor_capacity = 1000

    sim_opts = PandemicSimOpts(infection_spread_rate_mean=spread_rate)
    sim = make_sim(sim_opts, sim_non_cli_opts, numpy_rng=numpy_rng)

    # using swedish stage 1 regulation with the given social distancing to calibrate
    covid_regulation = dataclasses.replace(swedish_regulations[1], social_distancing=social_distancing)
    sim.execute_regulation(regulation=covid_regulation)

    hospital_ids = sim.registry.location_ids_of_type(Hospital)
    hospital_weekly = 0

    for i in trange(max_episode_length, desc='Simulating day'):
        sim.step_day()
        state = sim.state
        num_deaths = state.global_infection_summary[InfectionSummary.DEAD]
        deaths.append(num_deaths)
        num_hospitalizations = sum([cast(HospitalState, state.id_to_location_state[loc_id]).num_admitted_patients
                                    for loc_id in hospital_ids])
        hospital_weekly += num_hospitalizations
        if i % 7 == 0:
            hospitalizations.append(hospital_weekly)
            hospital_weekly = 0
    deaths_arr = np.asarray(deaths)
    deaths_arr = deaths_arr[1:] - deaths_arr[:-1]

    hosp_arr = np.asarray(hospitalizations)
    hosp_arr = hosp_arr[1:] - hosp_arr[:-1]

    eval_result = CalibrationData(deaths=deaths_arr, hospitalizations=hosp_arr)

    return eval_result if eval_result.is_valid() else eval_params(params, max_episode_length, trial_cnt=trial_cnt + 1)


def real_world_data() -> CalibrationData:
    """Extract and treat real-world data from WHO

    :returns: real-world death data
    """
    # using Sweden's death and hospitalization data
    deaths_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/new_deaths.csv'
    deaths_df = read_csv(deaths_url, header=0)
    real_deaths = deaths_df['Sweden'].values
    real_deaths = real_deaths[~np.isnan(real_deaths)]

    hosp_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/' \
               'COVID-2019%20-%20Hospital%20&%20ICU.csv'
    hosp_df = read_csv(hosp_url, header=0)
    real_hosp = np.array(hosp_df[hosp_df['entity'] == 'Sweden']['Weekly new ICU admissions'])
    real_hosp = np.round(real_hosp[~np.isnan(real_hosp)]).astype('int')
    return CalibrationData(deaths=real_deaths, hospitalizations=np.asarray(real_hosp))


def process_data(data: np.ndarray, data_len: Optional[int] = None, five_day_average: bool = False) -> np.ndarray:
    # trim initial zeros
    data = np.trim_zeros(data, 'f')[:data_len]

    # calculate sliding average
    if five_day_average:
        data = np.convolve(data, np.ones(5) / 5, mode='same')

    # normalize
    data = data / np.max(data)

    return data


def obj_func(params: np.ndarray) -> float:
    """Objective function calculates fitness score for a given parameter set

    :param params: spread rate and social distancing rate to be evaluated
    :returns: fitness score of parameter set
    """
    # get sim data
    sim_result: CalibrationData = eval_params(params, 60)
    sim_data = process_data(sim_result.hospitalizations)

    # get real data
    real_result: CalibrationData = real_world_data()
    real_data = process_data(real_result.hospitalizations, data_len=len(sim_data))

    # compare only until the rise of real_peak
    real_peak = np.argmax(real_data).item()
    real_data = real_data[:real_peak + 1]
    sim_data = sim_data[:real_peak + 1]

    # get score
    score = np.linalg.norm(real_data - sim_data)

    print('score: ', score)
    return float(score)


def make_plots(params: np.ndarray) -> None:
    """Plot final parameter set output against real world data

    :param params: resulting spread rate and social distancing rate
    """

    # get sim data
    sim_result: CalibrationData = eval_params(params, 100)
    sim_data = process_data(sim_result.hospitalizations)

    # get real data
    real_result: CalibrationData = real_world_data()
    real_data = process_data(real_result.hospitalizations, len(sim_data))

    # plot calibrated simulator run against real-world data
    plt.plot(sim_data)
    plt.plot(real_data)
    plt.legend(["PANDEMICSIM", "Sweden"])
    plt.xlabel("Weeks Passed")
    plt.ylabel("Hospitalizations Per Day (normalized)")
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
