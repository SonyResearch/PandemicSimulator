# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from typing import cast

import pandemic_simulator as ps


def simple_loop() -> None:
    ps.init_globals()

    work = ps.env.Office()
    home = ps.env.Home()

    person = ps.env.Worker(ps.env.PersonID('worker', age=35),
                           home=home.id,
                           work=work.id,
                           work_time=cast(ps.env.NonEssentialBusinessLocationState, work.state).open_time)

    sim = ps.env.PandemicSim([work, home], [person])

    for i in range(4):
        sim.step_day()
        print(sim.registry.global_location_summary)


def simple_work_loop() -> None:
    ps.init_globals()

    work = ps.env.Office()
    store = ps.env.GroceryStore()
    home = ps.env.Home()

    routines = [
        ps.sh.triggered_routine(None, ps.env.GroceryStore, 3),
    ]

    person = ps.env.Worker(ps.env.PersonID('worker', age=35), home=home.id, work=work.id,
                           work_time=cast(ps.env.NonEssentialBusinessLocationState, work.state).open_time,
                           outside_work_routines=routines)

    sim = ps.env.PandemicSim([work, store, home], [person])

    for i in range(4):
        sim.step_day()
        for (loc, _), summ in sim.registry.global_location_summary.items():
            print(f'{loc}: entry_count:{summ.entry_count}, visitor_count: {summ.visitor_count}')
        print('')


if __name__ == '__main__':
    simple_work_loop()
