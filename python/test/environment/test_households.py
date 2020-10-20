import numpy as np

from pandemic_simulator.environment import PopulationParams, CityRegistry, Home, GroceryStore, Office, School, \
    Hospital, \
    LocationParams
from pandemic_simulator.script_helpers import make_us_age_population, make_standard_locations

sample_population_params = PopulationParams(
    num_persons=50,
    location_type_to_params={
        Home: LocationParams(num=15),
        GroceryStore: LocationParams(num=5, worker_capacity=5, visitor_capacity=30),
        Office: LocationParams(num=5, worker_capacity=200, visitor_capacity=0),
        School: LocationParams(num=5, worker_capacity=40, visitor_capacity=300),
        Hospital: LocationParams(num=5, worker_capacity=30, visitor_capacity=2),
    })


def test_family_households():
    population_params = sample_population_params
    numpy_rng = np.random.RandomState()
    cr = CityRegistry()

    locations = make_standard_locations(population_params, registry=cr, numpy_rng=numpy_rng)
    persons = make_us_age_population(population_params, registry=cr, numpy_rng=numpy_rng)

    for per in persons:
        person = per.id
        if person.age <= 18:
            home_id = cr.get_person_home_id(person)
            print(f'house id: {home_id}')
            household = cr.get_persons_in_location(home_id)
            has_adult = False
            for member in household:
                print(f'house id: {home_id} member age: {member.age}')
                if 18 < member.age <= 65:
                    has_adult = True
            assert has_adult


def test_retiree_households():
    population_params = sample_population_params
    numpy_rng = np.random.RandomState()
    cr = CityRegistry()

    locations = make_standard_locations(population_params, registry=cr, numpy_rng=numpy_rng)
    persons = make_us_age_population(population_params, registry=cr, numpy_rng=numpy_rng)

    home_ids = cr.location_ids_of_type(Home)
    retired_homes = int(float(len(home_ids)) * 0.15)
    home_iter = len(home_ids) - retired_homes
    only_retirees = True
    while home_iter < len(home_ids):
        household = cr.get_persons_in_location(home_ids[home_iter])
        for member in household:
            if member.age <= 65:
                only_retirees = False
        home_iter += 1
        assert only_retirees
