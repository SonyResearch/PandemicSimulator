# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from typing import cast

import numpy as np

import pandemic_simulator as ps
from pandemic_simulator.script_helpers import triggered_routine


def simple_loop() -> None:
    cr = ps.env.CityRegistry()

    work = ps.env.Office(ps.env.LocationID('office'), cr, init_state=ps.env.NonEssentialBusinessLocationState(
        open_time=ps.env.SimTimeTuple(hours=tuple(range(9, 17)))))
    home = ps.env.Home(ps.env.LocationID('home'), cr)

    person = ps.env.Worker(ps.env.PersonID('worker', age=35), home=home.id, work=work.id, registry=cr,
                           work_time=cast(ps.env.NonEssentialBusinessLocationState, work.state).open_time)

    sim = ps.env.PandemicSim(cr, [work, home], [person])

    for i in range(4):
        sim.step_day()
        print(cr.global_location_summary)


def simple_work_loop() -> None:
    rng = np.random.RandomState(0)

    cr = ps.env.CityRegistry()

    work = ps.env.Office(ps.env.LocationID('office'),
                         cr,
                         init_state=ps.env.NonEssentialBusinessLocationState(
                             open_time=ps.env.SimTimeTuple(hours=tuple(range(9, 17)))),
                         numpy_rng=rng)
    store = ps.env.GroceryStore(ps.env.LocationID('grocery'),
                                cr,
                                init_state=ps.env.BusinessLocationState(
                                    open_time=ps.env.SimTimeTuple(hours=tuple(range(8, 20)))),
                                numpy_rng=rng)
    home = ps.env.Home(ps.env.LocationID('home'), cr, numpy_rng=rng)

    routines = [
        triggered_routine(cr, None, ps.env.GroceryStore, 3, numpy_rng=rng),
    ]

    person = ps.env.Worker(ps.env.PersonID('worker', age=35), home=home.id, work=work.id, registry=cr,
                           work_time=cast(ps.env.NonEssentialBusinessLocationState, work.state).open_time,
                           outside_work_routines=routines, numpy_rng=rng)

    sim = ps.env.PandemicSim(cr, [work, store, home], [person])

    for i in range(4):
        sim.step_day()
        print(cr.global_location_summary)


if __name__ == '__main__':
    simple_work_loop()
