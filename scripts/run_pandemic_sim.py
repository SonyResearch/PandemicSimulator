# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
import numpy as np
from tqdm import trange

from pandemic_simulator.environment import austin_regulations, Hospital, PandemicSimOpts, PandemicSimNonCLIOpts
from pandemic_simulator.script_helpers import small_town_population_params, make_sim
from pandemic_simulator.viz import MatplotLibViz

if __name__ == '__main__':
    # setup rng
    numpy_rng = np.random.RandomState(seed=100)

    # setup simulator options sets
    sim_opts = PandemicSimOpts()
    sim_non_cli_opts = PandemicSimNonCLIOpts(small_town_population_params)

    # make sim
    sim = make_sim(sim_opts, sim_non_cli_opts, numpy_rng=numpy_rng)

    # setup viz
    viz = MatplotLibViz(num_persons=sim_non_cli_opts.population_params.num_persons,
                        hospital_params=sim_non_cli_opts.population_params.location_type_to_params[Hospital],
                        num_stages=len(austin_regulations),
                        show_stages=False)

    # run regulation stpes in the simulator
    stage_to_regulation = {reg.stage: reg for reg in austin_regulations}
    for i in trange(2, desc='Simulating day'):
        # get the regulation
        regulation = stage_to_regulation[0]  # stage 0

        # execute the given regulation
        sim.execute_regulation(regulation=regulation)

        for _ in range(sim_opts.sim_steps_per_regulation):
            # step sim
            sim.step()

        # get state
        state = sim.state

        # visualize
        viz.record(state)

    # generate plots
    viz.plot()
