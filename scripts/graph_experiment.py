# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from sys import stdout
from typing import List

import numpy as np
from matplotlib import pyplot as plt
from numpy import max

from pandemic_simulator.environment import austin_regulations, PandemicSimOpts, PandemicSimNonCLIOpts
from pandemic_simulator.script_helpers import small_town_population_params, make_sim
from pandemic_simulator.viz import GraphViz


def run(days: int, stage: int, days_per_interval: int) -> List[int]:
    # setup rng
    numpy_rng = np.random.RandomState(seed=100)

    # setup simulator options sets
    sim_opts = PandemicSimOpts(use_contact_tracer=True)
    sim_non_cli_opts = PandemicSimNonCLIOpts(small_town_population_params)

    # make sim
    sim = make_sim(sim_opts, sim_non_cli_opts, numpy_rng=numpy_rng)

    # setup viz
    viz = GraphViz(sim, num_stages=len(austin_regulations), days_per_interval=days_per_interval)

    # run regulation stpes in the simulator
    stage_to_regulation = {reg.stage: reg for reg in austin_regulations}
    print(f'Stage {stage}:')
    for _ in range(100):
        print(f'{sim.state.sim_time.day + 1} ', end='')
        stdout.flush()

        # get the regulation
        regulation = stage_to_regulation[stage]  # stage 0

        # execute the given regulation
        sim.execute_regulation(regulation=regulation)

        for i in range(sim_opts.sim_steps_per_regulation):
            # step sim
            sim.step()

        # get state
        state = sim.state

        # visualize
        viz.record(state)

    # generate plots
    # viz.plot()

    return viz._num_components_per_interval


if __name__ == '__main__':
    title = "2-Week Interval"
    days_per_interval = 14

    stage_results = []
    for stage in range(0, 5):
        stage_results.append(run(days=100, stage=stage, days_per_interval=days_per_interval))

    plt.figure(figsize=(12, 8))

    for i in range(0, len(stage_results)):
        plt.plot(stage_results[i], label="Stage " + str(i))

    plt.ylim([-0.1, max(stage_results) + 1])
    plt.title('Connected Components by ' + title)
    plt.xlabel('time (' + title.lower() + 's)')
    plt.legend()

    plt.show()
