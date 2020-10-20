# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
import copy

import numpy as np

from pandemic_simulator.environment import CityRegistry, Home, GroceryStore, Office, School, Hospital, PopulationParams, \
    LocationParams
from pandemic_simulator.script_helpers import make_standard_locations, make_us_age_population

tiny_population_params = PopulationParams(
    num_persons=10,
    location_type_to_params={
        Home: LocationParams(num=3),
        GroceryStore: LocationParams(num=1, worker_capacity=5, visitor_capacity=30),
        Office: LocationParams(num=1, worker_capacity=200, visitor_capacity=0),
        School: LocationParams(num=1, worker_capacity=40, visitor_capacity=300),
        Hospital: LocationParams(num=1, worker_capacity=30, visitor_capacity=2),
    })


def test_location_and_person_reset():
    population_params = tiny_population_params
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
