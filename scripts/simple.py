# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from typing import cast

import pandemic_simulator as ps


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
        print(cr.global_location_summary[('Office', 'Worker')])


if __name__ == '__main__':
    simple_loop()
