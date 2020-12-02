import copy
import GPyOpt

import numpy as np
from pandas import read_csv
from tqdm import trange

import matplotlib.pyplot as plt

from pandemic_simulator.script_helpers.population_params import above_medium_town_population_params
from pandemic_simulator.script_helpers import EvaluationOpts, make_sim
from pandemic_simulator.environment import PandemicSim, PandemicSimOpts, PandemicSimNonCLIOpts, PandemicRegulation, PandemicSimState, InfectionSummary

def eval_params(opts: EvaluationOpts) -> np.ndarray:
    '''Perform a single run of the simulator.'''
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

def run_sim(params: np.ndarray)->np.ndarray:
    '''Prepare paramaters, run sim, treat output'''
    opts = EvaluationOpts(
        num_seeds = 30,
        spread_rates = params[:, 0],
        social_distancing = params[:, 1],
        max_episode_length=110,
    )

    try:
        sim_data = eval_params(opts=opts)
    except ValueError:
        pass

    sim_data = treat_sim_data(data=sim_data, num_days=opts.max_episode_length)

    return sim_data

def real_world_data():
    '''Extract and treat real-world data from WHO'''
    global real_data
    global real_peak

    #using Sweden's death data
    deaths_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/new_deaths.csv'
    deaths_df = read_csv(deaths_url, header=0)
    real_data = deaths_df['Sweden'].values

    #start at first death
    real_data = np.trim_zeros(real_data, 'f')
    real_data = real_data[~np.isnan(real_data)]

    #calculate sliding average
    ma_vec = np.cumsum(real_data, dtype=float)
    ma_vec[5:] = ma_vec[5:] - ma_vec[:-5]
    real_data = ma_vec[5 - 1:] / 5

    #calculate peak
    real_peak = np.argmax(real_data).item()
    
    #normalize
    real_data /= real_data[real_peak] 


def least_diff(world_data: np.ndarray, sim_data: np.ndarray)-> float:
    '''Calculate sum difference over the rises of the two curves.'''
    score = 0
    for j in range(min(len(world_data), len(sim_data))):
        score += abs(world_data[j] - sim_data[j])
    return score

def treat_sim_data(data: np.ndarray, num_days: int) -> np.ndarray:
    '''Treat simulator output.'''
    #extract deaths per day
    temp = copy.deepcopy(data)
    for j in range(num_days-1):
        temp[j+1]= temp[j+1]-data[j]
    data = copy.deepcopy(temp)

    #start at first death
    data = data[next((i for i, x in enumerate(data) if x), None):] 
    
    #calculate sliding average
    ma_vec = np.cumsum(data, dtype=float)
    ma_vec[5:] = ma_vec[5:] - ma_vec[:-5]
    data = ma_vec[5 - 1:] / 5

    print(data)
    return data 

def obj_func(params: np.ndarray) -> float:
    '''Objective function takes in a spread rate and a social distancing rate, outputs fitness score'''
    sim_data = run_sim(params)

    #calculate peak score
    sim_peak = np.argmax(sim_data).item()
    peak_score = abs(sim_peak - real_peak) 

    #normalize
    sim_data /= sim_data[sim_peak] 

    #calculate least difference over rise of curve
    rise_score = least_diff(world_data=real_data[:real_peak], sim_data=sim_data[:sim_peak])

    print('score: ', rise_score+peak_score)
    return rise_score+peak_score

def make_plots(params: np.ndarray):
    '''Plot final parameter set output against real world data.'''
    sim_data = run_sim(params)

    #normalize
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
    real_world_data()

    bounds2d = [{'name': 'spread rate', 'type': 'continuous', 'domain': (0.005,0.03)},
                {'name': 'contact rate', 'type': 'continuous', 'domain': (0.,0.8)}]
    maxiter = 20
    myBopt_2d = GPyOpt.methods.BayesianOptimization(obj_func, domain=bounds2d)
    myBopt_2d.run_optimization(max_iter=maxiter)
    
    print("="*20)
    print("Value of (spread rate, contact rate) that minimises the objective:"+str(myBopt_2d.x_opt))    
    print("Minimum value of the objective: "+str(myBopt_2d.fx_opt))     
    print("="*20)

    make_plots(np.array([[myBopt_2d.x_opt[0], myBopt_2d.x_opt[1]]], dtype=np.float64))