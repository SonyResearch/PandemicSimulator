# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from tqdm import trange

import pandemic_simulator as ps


def using_sim_config() -> None:
    """In simple_worker tutorials, we created each person and location manually. However, this can become tedious if
    we want to generate a large population. To remedy this, the simulator provides a config interface and this
    tutorial shows how to use it."""

    print('\nA tutorial to use PandemicSimConfig', flush=True)

    # the first thing to do at the start of any experiment is to initialize a few global parameters
    # these parameters are shared across the entire repo
    ps.init_globals()

    # generate a simulator config (see `python/pandemic_simulator/script_helpers/sim_configs.py` for more configs)
    sim_config = ps.env.PandemicSimConfig(
        num_persons=10,
        location_configs=[
            ps.env.LocationConfig(location_type=ps.env.Home, num=3),
            ps.env.LocationConfig(location_type=ps.env.GroceryStore, num=1),
            ps.env.LocationConfig(location_type=ps.env.Office, num=1),
            ps.env.LocationConfig(location_type=ps.env.School, num=1)
        ])

    # Init simulator
    sim = ps.env.PandemicSim.from_config(sim_config)

    # Iterate by advancing in days by calling step_day in the simulator
    for _ in trange(10, desc='Simulating day'):
        sim.step_day()


if __name__ == '__main__':
    using_sim_config()
