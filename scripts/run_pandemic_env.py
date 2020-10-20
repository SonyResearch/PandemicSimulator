# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

import numpy as np
from tqdm import trange

from pandemic_simulator.environment import Hospital, PandemicSimOpts, PandemicSimNonCLIOpts, austin_regulations
from pandemic_simulator.script_helpers import small_town_population_params, make_gym_env
from pandemic_simulator.viz import MatplotLibViz

if __name__ == '__main__':
    # setup rng
    numpy_rng = np.random.RandomState(seed=100)

    # setup simulator options sets
    sim_opts = PandemicSimOpts()
    sim_non_cli_opts = PandemicSimNonCLIOpts(small_town_population_params)

    # make env
    pandemic_regulations = austin_regulations
    env = make_gym_env(sim_opts, sim_non_cli_opts, pandemic_regulations=pandemic_regulations, numpy_rng=numpy_rng)

    # setup viz
    viz = MatplotLibViz(num_persons=sim_non_cli_opts.population_params.num_persons,
                        hospital_params=sim_non_cli_opts.population_params.location_type_to_params[Hospital],
                        num_stages=len(pandemic_regulations),
                        show_stages=False)

    # run stage-0 action steps in the environment
    env.reset()
    for i in trange(100, desc='Simulating day'):
        obs, reward, done, aux = env.step(0)  # stage 0
        viz.record(obs, reward=reward)

    # generate plots
    viz.plot()
