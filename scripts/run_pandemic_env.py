# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from tqdm import trange

import pandemic_simulator as ps

if __name__ == '__main__':
    # init globals
    ps.init_globals(seed=100)

    # select a simulator config
    sim_config = ps.sh.small_town_config

    # make env
    pandemic_regulations = ps.sh.austin_regulations
    env = ps.sh.make_gym_env(sim_config, pandemic_regulations=pandemic_regulations)

    # setup viz
    viz = ps.viz.MatplotLibViz(num_persons=sim_config.num_persons,
                               max_hospital_capacity=sim_config.max_hospital_capacity,
                               num_stages=len(ps.sh.austin_regulations),
                               show_stages=False)

    # run stage-0 action steps in the environment
    env.reset()
    for i in trange(10, desc='Simulating day'):
        obs, reward, done, aux = env.step(0)  # stage 0
        viz.record(obs, reward=reward)

    # generate plots
    viz.plot()
