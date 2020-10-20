# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

import pytest

from pandemic_simulator.environment import Office, CityRegistry, PopulationParams, LocationParams, Home, Minor, \
    Worker, School


@pytest.fixture
def population_params():
    return PopulationParams(num_persons=10,
                            location_type_to_params={Office: LocationParams(2, 5),
                                                     Home: LocationParams(5),
                                                     School: LocationParams(1)})


def city_registry(params):
    registry = CityRegistry()
    location_type_to_params = params.location_type_to_params
    _ = [Home(name=f'home_{i}', registry=registry) for i in range(location_type_to_params[Home].num)]
    _ = [School(name=f'school_{i}', registry=registry) for i in range(location_type_to_params[School].num)]
    _ = [Office(name=f'office_{i}', registry=registry) for i in range(location_type_to_params[Office].num)]
    return registry


def test_register_persons(population_params):
    registry = city_registry(population_params)
    home_id = registry.location_ids_of_type(Home)[0]
    school_id = registry.location_ids_of_type(School)[0]
    office_id = registry.location_ids_of_type(Office)[0]
    m = Minor(3, home_id, registry=registry, school=school_id, name='minor_0')
    a = Worker(36, home_id, registry=registry, work=office_id, name='adult_0')

    assert (m.id in registry.get_persons_in_location(home_id))
    assert (a.id in registry.get_persons_in_location(home_id))
