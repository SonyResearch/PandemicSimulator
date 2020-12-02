# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
import copy

import numpy as np

from pandemic_simulator.environment import CityRegistry
from pandemic_simulator.script_helpers import make_standard_locations, make_us_age_population, \
    tiny_town_population_params


def test_location_and_person_reset():
    population_params = tiny_town_population_params
    numpy_rng = np.random.RandomState(0)

    cr = CityRegistry()
    locations = make_standard_locations(population_params, registry=cr, numpy_rng=numpy_rng)
    persons = make_us_age_population(population_params, registry=cr, numpy_rng=numpy_rng)

    loc_states = [copy.deepcopy(loc.state) for loc in locations]
    per_states = [copy.deepcopy(per.state) for per in persons]

    for loc in locations:
        loc.reset()

    for per in persons:
        per.reset()

    new_loc_states = [copy.deepcopy(loc.state) for loc in locations]
    new_per_states = [copy.deepcopy(per.state) for per in persons]

    for st1, st2 in zip(loc_states, new_loc_states):
        assert st1 == st2

    for st1, st2 in zip(per_states, new_per_states):
        assert st1 == st2
