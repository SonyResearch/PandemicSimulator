# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from tqdm import trange

import pandemic_simulator as ps

if __name__ == '__main__':
    # init globals
    ps.init_globals(seed=100)

    # select a simulator config
    sim_config = ps.sh.small_town_config

    # make sim
    sim = ps.sh.make_sim(sim_config)

    # setup viz
    viz = ps.viz.MatplotLibViz(num_persons=sim_config.num_persons,
                               max_hospital_capacity=sim_config.max_hospital_capacity,
                               num_stages=len(ps.sh.austin_regulations),
                               show_stages=False)

    # execute a regulation
    sim.impose_regulation(regulation=ps.sh.austin_regulations[0])  # stage 0

    # run regulation steps in the simulator
    for _ in trange(100, desc='Simulating day'):
        sim.step_day()
        viz.record(sim.state)

    # generate plots
    viz.plot()
