# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from tqdm import trange

import pandemic_simulator as ps

if __name__ == '__main__':
    # init globals
    ps.init_globals(seed=100)

    # setup simulator config and options
    sim_config = ps.sh.small_town_config
    sim_opts = ps.env.PandemicSimOpts()  # use defaults

    # make sim
    sim = ps.sh.make_sim(sim_config, sim_opts)

    # setup viz
    viz = ps.viz.MatplotLibViz(num_persons=sim_config.num_persons,
                               max_hospital_capacity=sim_config.max_hospital_capacity,
                               num_stages=len(ps.sh.austin_regulations),
                               show_stages=False)

    # execute a regulation
    sim.execute_regulation(regulation=ps.sh.austin_regulations[0])  # stage 0

    # run regulation steps in the simulator
    for _ in trange(100, desc='Simulating day'):
        sim.step_day()
        viz.record(sim.state)

    # generate plots
    viz.plot()
