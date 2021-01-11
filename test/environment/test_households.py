import numpy as np

import pandemic_simulator as ps


def test_family_households():
    ps.init_globals()
    config = ps.sh.small_town_config
    cr = ps.env.globals.registry

    ps.env.make_locations(config)
    ps.env.make_population(config)

    retiree_homes = []
    minor_homes = []
    adult_homes = []

    homes = cr.location_ids_of_type(ps.env.Home)

    tot_persons = 0
    for home in homes:
        household = cr.get_persons_in_location(home)

        adults = 0
        minors = 0
        retirees = 0
        for member in household:
            if member.age <= 18:
                minors += 1
            elif 18 < member.age <= 65:
                adults += 1
            else:
                retirees += 1
        if minors > 0:
            minor_homes.append([minors, adults, retirees])
        elif adults > 0:
            adult_homes.append([minors, adults, retirees])
        else:
            retiree_homes.append([minors, adults, retirees])
        tot_persons += len(household)

    assert len(minor_homes)
    assert len(adult_homes)
    assert len(retiree_homes)
    assert tot_persons == config.num_persons

    minor_homes = np.asarray(minor_homes)
    adult_homes = np.asarray(adult_homes)
    retiree_homes = np.asarray(retiree_homes)

    # there should be non-zero homes with 1, 2, and 3 children
    for i in range(1, 4):
        assert len(minor_homes[minor_homes[:, 0] == i]) > 0

        # each minor home must contain an adult
    for home in minor_homes:
        assert home[1] > 0

    # minor homes in general must also have retirees for small town config
    assert np.sum(minor_homes, axis=0)[2] > 0

    # there should be non-zeros homes with 1 and >1 adults
    assert len(adult_homes[adult_homes[:, 1] == 1]) > 0
    assert len(adult_homes[adult_homes[:, 1] > 1]) > 0

    # no minors in adult homes
    assert np.sum(adult_homes, axis=0)[0] == 0

    # adult homes in general must also have retirees for small town config
    assert np.sum(adult_homes, axis=0)[2] > 0

    # there should be non-zeros with only retirees and no adults and minors
    assert np.sum(retiree_homes, axis=0)[2] > 0
    assert np.sum(retiree_homes, axis=0)[1] == 0
    assert np.sum(retiree_homes, axis=0)[0] == 0


def test_retiree_households():
    ps.init_globals()
    config = ps.sh.small_town_config

    ps.env.make_locations(config)
    ps.env.make_population(config)

    cr = ps.env.globals.registry

    home_ids = cr.location_ids_of_type(ps.env.Home)
    retirees_in_nursing_home = 0
    all_retirees = 0
    for home in home_ids:
        household = cr.get_persons_in_location(home)
        is_nursing_home = True
        for member in household:
            if member.age <= 65:
                is_nursing_home = False
            else:
                all_retirees += 1
        if is_nursing_home:
            retirees_in_nursing_home += len(household)

    assert (retirees_in_nursing_home / all_retirees) > 0.065
