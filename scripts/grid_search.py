import numpy as np
import copy

from mpl_toolkits import mplot3d
# %matplotlib inline
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

from scipy.signal import find_peaks
from pandas import read_csv

from covid19.script_helpers.population_params import medium_town_population_params
from covid19.script_helpers import EvaluationOpts, evaluate_spread_rates, \
    make_evaluation_plots, experiment_main
from covid19.data import H5DataSaver, H5DataLoader, StageSchedule
from covid19.environment import CovidSimOpts, CovidSimNonCLIOpts, CovidRegulation, DEFAULT_REGULATION, sorted_infection_summary, InfectionSummary


def eval_params(experiment_name: str, opts: EvaluationOpts):
    sim_non_cli_opts = CovidSimNonCLIOpts(medium_town_population_params)
    data_saver = H5DataSaver(experiment_name, path=opts.data_saver_path)
    for i, spread_rate in enumerate(opts.spread_rates):
        sim_opts = CovidSimOpts(infection_spread_rate_mean=spread_rate)
        covid_regulations = [CovidRegulation(social_distancing=sd)
                         for sd in opts.social_distancing]
        for j, cr in enumerate(covid_regulations):
            print(f'Running with spread rate: {spread_rate} and social distancing: {cr.social_distancing}')
            id = i*(len(opts.social_distancing)) + j
            experiment_main(sim_opts=sim_opts,
                            sim_non_cli_opts=sim_non_cli_opts,
                            data_saver=data_saver,
                            covid_regulations=covid_regulations,
                            stages_to_execute=opts.strategies,
                            num_random_seeds=opts.num_seeds,
                            max_episode_length=opts.max_episode_length,
                            exp_id=id)

def time_to_peak(test_peak: int, sim_peaks: np.ndarray, scores: np.ndarray, num_combos: int)-> np.ndarray:
    # best_score = 0
    for i in range(num_combos):
        curr_peak = sim_peaks[i]
        scores[i][1] = [abs(curr_peak-test_peak)]
        # if scores[i][1][0] < scores[best_score][1][0]:
        #     best_score = i
    # print('Time to Peak Test Result')
    # print('Best Score with Params: ', scores[best_score][0], '   Peak Difference: ', scores[best_score][1][0])
    return scores

def least_diff(test_data: np.ndarray, sim_data: np.ndarray, scores: np.ndarray, num_combos: int)-> np.ndarray:
    # best_score = 0
    for i in range(num_combos):
        combo_score = 0
        arr_len = min(len(test_data), len(sim_data[i]))
        for j in range(arr_len):
            combo_score += abs(test_data[j] - sim_data[i][j])
        scores[i][1]=[combo_score]
        # if combo_score < scores[best_score][1][0]:
        #     best_score = i
    # print('Difference Test Result')
    # print('Best Score with Params: ', scores[best_score][0], '   Difference Sum: ', scores[best_score][1][0])
    return scores

def treat_sim_data(data: np.ndarray, num_days: int) -> np.ndarray:
    for i in range(len(data)):
        #extract global testing summary
        data[i] = data[i].obs_trajectories.global_testing_summary[1:]
        cases= np.ndarray((num_days,), np.float64)
        #extract deaths
        gis_legend = [summ.value for summ in sorted_infection_summary]
        deaths_index = gis_legend.index(InfectionSummary.DEAD.value)
        for j in range(num_days):
            cases[j]=data[i][:, deaths_index][j][1]
        data[i]=cases
    #modify data to deaths per day
    temp = copy.deepcopy(data)
    for i in range(len(data)):
        for j in range(num_days-1):
            temp[i][j+1]= temp[i][j+1]-data[i][j]
    data = copy.deepcopy(temp)
    return data

def normalize_scores(scores: np.ndarray) -> np.ndarray:
    scores = scores[:,1]
    scores = [y for x in scores for y in x]
    norm = np.linalg.norm(scores)
    scores = scores/norm
    return scores

def score_data(sim_data: np.ndarray, test_data: np.ndarray, scores: np.ndarray, num_combos: int) -> np.ndarray:
    #get time to peak
    test_peak = find_peaks(test_data, height=100, threshold=None, distance=10, prominence=None, width=None, wlen=None, rel_height=0.5, plateau_size=None)[0][0]
    sim_peaks = np.ndarray((num_combos,),int)
    for i in range(num_combos): #TODO: change height for sim
        sim_peaks[i] = find_peaks(sim_data[i], height=4, threshold=None, distance=5, prominence=None, width=None, wlen=None, rel_height=0.5, plateau_size=None)[0][0]
    peak_scores = time_to_peak(test_peak=test_peak, sim_peaks=sim_peaks, scores=copy.deepcopy(scores), num_combos=num_combos)
    #normalize death data
    test_data/=10000000 #need exact data?
    for i in range(len(sim_data)):
        sim_data[i]/=4000
    #alter data to start at peak for tail fit
    test_data = test_data[test_peak:]
    for i in range(len(sim_data)):
        sim_data[i] = sim_data[i][sim_peaks[i]:]
    #fit tail with least difference
    tail_scores = least_diff(test_data=test_data, sim_data=sim_data, scores=copy.deepcopy(scores), num_combos=num_combos)
    #normalize scores
    peak_scores = normalize_scores(peak_scores)
    tail_scores = normalize_scores(tail_scores)
    #scale data and calculate final scores
    best_score = 0
    for i in range(len(scores)):
        scores[i][1][0] = tail_scores[i] + peak_scores[i]
        if(scores[i][1][0] < scores[best_score][1][0]):
            best_score = i
    print('Best score combo: ', scores[best_score][0], '     Score: ', scores[best_score][1])
    return scores

def extract(list: np.ndarray, pos: int):
    return[item[pos] for item in list]

if __name__ == '__main__':
    spread_rates = (0.01, 0.02, 0.03)
    social_distancing = (0.1, 0.3, 0.5)
    num_combos = len(spread_rates)*len(social_distancing) #number of possible grid squares
    def_strategy = [StageSchedule(stage=0, end_day=None)]
    num_days = 120
    num_seeds = 5 
    opts = EvaluationOpts(
        num_seeds = num_seeds,
        spread_rates = spread_rates,
        social_distancing = social_distancing,
        strategies = def_strategy,
        max_episode_length=num_days,
        enable_warm_up=False,
    )

    #create array of param combinations
    combos_arr = np.ndarray((num_combos,),np.ndarray)
    for i, sr in enumerate(spread_rates):
        for j, sd in enumerate(social_distancing):
            combos_arr[i*len(social_distancing)+j] = [spread_rates[i], social_distancing[j]]
    
    exp_name = 'parameter_optimization'
    try:
        eval_params(experiment_name=exp_name, opts=opts)
    except ValueError:
        pass
    loader = H5DataLoader('parameter_optimization', opts.data_saver_path)
    data = list(loader.get_data())
    
    #extract deaths per day from sim results
    data = treat_sim_data(data=data, num_days=num_days)
    
    #extract deaths per day from real-world data
    deaths_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/new_deaths.csv'
    cases_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/new_cases.csv' #cases per day data
    deaths_df = read_csv(deaths_url, header=0)
    test_data = deaths_df['Sweden'].values
    cases_df = read_csv(cases_url, header=0)
    cases_test_data = cases_df['Sweden'].values
    i = 0
    while cases_test_data[i] == 0: #modify to start at first infection
        i+=1
    test_data = test_data[i:]

    # scores array: column 1 is array of param combos, column 2 is score (initialized to 0)
    scores = []
    for i in range(num_combos): #expand to multidimensional array
        scores.append([combos_arr[i], [0]])
    scores = np.asarray(scores, dtype=object)
    scores = score_data(test_data=test_data, sim_data=data, scores=scores, num_combos=num_combos)


    # fig = plt.figure()
    # ax = plt.axes(projection='3d')
    # X = extract(scores[:,0], 0)
    # Y = extract(scores[:,0], 1)
    # Z = extract(scores[:,1], 0)

    # ax.scatter3D(X, Y, Z, c=Z, cmap='Greens')
    # plt.show()

    # param_labels = ['0.01, 0.1', '0.01, 0.3', '0.01, 0.5','0.02, 0.1', '0.02, 0.3', '0.02, 0.5','0.03, 0.1', '0.03, 0.3', '0.03, 0.5',]
    # make_evaluation_plots(exp_name=exp_name, data_saver_path=opts.data_saver_path, param_labels=combos_arr,
    #                 bar_plot_xlabel='Spread Rates, Contact Rates', show_cumulative_reward=False,
    #                 show_time_to_peak=False, show_pandemic_duration=False, annotate_stages = True)

    # plt.show()