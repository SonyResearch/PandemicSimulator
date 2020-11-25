import copy
from scipy.signal import find_peaks

import GPyOpt

import numpy as np
import sys
from pandas import read_csv
from tqdm import trange

#Plotting tools
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm

from pandemic_simulator.script_helpers.population_params import above_medium_town_population_params
from pandemic_simulator.script_helpers import EvaluationOpts, make_evaluation_plots, make_sim
from pandemic_simulator.environment import PandemicSim, PandemicSimOpts, PandemicSimNonCLIOpts, PandemicRegulation, PandemicSimState, InfectionSummary

def eval_params(experiment_name: str, opts: EvaluationOpts) -> np.ndarray:
    deaths = []
    numpy_rng = np.random.RandomState(seed = opts.num_seeds)
    sim_non_cli_opts = PandemicSimNonCLIOpts(above_medium_town_population_params)
    sim_opts = PandemicSimOpts(infection_spread_rate_mean=opts.spread_rates)
    sim = make_sim(sim_opts, sim_non_cli_opts, numpy_rng=numpy_rng)
    covid_regulations = PandemicRegulation(social_distancing=opts.social_distancing, stage = 0)
    print(f'Running with spread rate: {opts.spread_rates} and social distancing: {opts.social_distancing}')
    for i in trange(opts.max_episode_length, desc='Simulating day'):
        sim.execute_regulation(regulation=covid_regulations)
        for j in trange(sim_opts.sim_steps_per_regulation):
            sim.step()
        state = sim.state
        num_deaths = state.global_infection_summary[InfectionSummary.DEAD]
        deaths = np.append(deaths, num_deaths)
    return deaths

#extract death data from WHO Sweden
def real_world_data()-> np.ndarray:
    global test_data
    global test_peak
    deaths_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/new_deaths.csv'
    deaths_df = read_csv(deaths_url, header=0)
    test_data = deaths_df['Sweden'].values

    #modify to start at first death
    test_data = np.trim_zeros(test_data, 'f')
    test_data = test_data[~np.isnan(test_data)]

    #calculate sliding average
    ma_vec = np.cumsum(test_data, dtype=float)
    ma_vec[5:] = ma_vec[5:] - ma_vec[:-5]
    test_data = ma_vec[5 - 1:] / 5

    #calculate peak
    test_peak = np.argmax(test_data).item()
    
    #normalize
    test_data /= test_data[test_peak] 

    #end at peak
    test_data = test_data[:test_peak]    
    return test_data

#take least difference score over rise
def least_diff(test_data: np.ndarray, sim_data: np.ndarray)-> float:
    score = 0
    arr_len = min(len(test_data), len(sim_data))
    for j in range(arr_len):
        score += abs(test_data[j] - sim_data[j])
    return score

#extract deaths per day for each simulator
def treat_sim_data(data: np.ndarray, num_days: int) -> np.ndarray:
    temp = copy.deepcopy(data)
    for j in range(num_days-1):
        temp[j+1]= temp[j+1]-data[j]
    data = copy.deepcopy(temp)
    index = next((i for i, x in enumerate(data) if x), None)
    data = data[index:] #start at first death
    
    #calculate sliding average
    ma_vec = np.cumsum(data, dtype=float)
    ma_vec[5:] = ma_vec[5:] - ma_vec[:-5]
    data = ma_vec[5 - 1:] / 5
    print(data)
    return data 
  
#function takes a spread rate and a contact rate and outputs fitness score
def calc_score(params: np.ndarray) -> float:
    spread_rate = params[:, 0]
    contact_rate = params[:, 1]
    num_days = 110
    num_seeds = 30
    opts = EvaluationOpts(
        num_seeds = num_seeds,
        spread_rates = spread_rate,
        social_distancing = contact_rate,
        max_episode_length=num_days,
    )

    exp_name = 'bayesian_opts_' + str(spread_rate) + '_' + str(contact_rate) 
    try:
        sim_data = eval_params(experiment_name=exp_name, opts=opts)
    except ValueError:
        pass

    sim_data = treat_sim_data(data=sim_data, num_days=num_days)
    
    #calculate peak score
    sim_peak = np.argmax(sim_data).item()
    peak_score = abs(sim_peak - test_peak)
    
    #normalize
    sim_data /= sim_data[sim_peak] 
    
    #end data at peak
    sim_data = sim_data[:sim_peak] 
   
    rise_score = least_diff(test_data=test_data, sim_data=sim_data)

    print('score: ', rise_score+peak_score)
    #TODO: Need better weighing of scores?
    return rise_score+peak_score



if __name__ == '__main__':
    #Using Sweden's death data
    real_world_data()

    bounds2d = [{'name': 'spread rate', 'type': 'continuous', 'domain': (0.005,0.03)},
                {'name': 'contact rate', 'type': 'continuous', 'domain': (0.,0.8)}]
    maxiter = 20

    myBopt_2d = GPyOpt.methods.BayesianOptimization(calc_score, domain=bounds2d)
    myBopt_2d.run_optimization(max_iter = maxiter)

    print("="*20)
    print("Value of (spread rate, contact rate) that minimises the objective:"+str(myBopt_2d.x_opt))    
    print("Minimum value of the objective: "+str(myBopt_2d.fx_opt))     
    print("="*20)
    myBopt_2d.plot_acquisition()
