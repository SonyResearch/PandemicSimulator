# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

import pytest

from pandemic_simulator.environment import Office, CityRegistry, PopulationParams, LocationParams, Home, Minor, \
    Worker, School, LocationID, PersonID


@pytest.fixture
def population_params():
    return PopulationParams(num_persons=10,
                            location_type_to_params={Office: LocationParams(2, 5),
                                                     Home: LocationParams(5),
                                                     School: LocationParams(1)})


def city_registry(params):
    registry = CityRegistry()
    location_type_to_params = params.location_type_to_params
    _ = [Home(loc_id=LocationID(f'home_{i}'), registry=registry) for i in range(location_type_to_params[Home].num)]
    _ = [School(loc_id=LocationID(f'school_{i}'), registry=registry)
         for i in range(location_type_to_params[School].num)]
    _ = [Office(loc_id=LocationID(f'office_{i}'), registry=registry)
         for i in range(location_type_to_params[Office].num)]
    return registry


def test_register_persons(population_params):
    registry = city_registry(population_params)
    home_id = registry.location_ids_of_type(Home)[0]
    school_id = registry.location_ids_of_type(School)[0]
    office_id = registry.location_ids_of_type(Office)[0]
    m = Minor(PersonID('minor_0', 3), home_id, school=school_id, registry=registry)
    a = Worker(PersonID('adult_0', 36), home_id, work=office_id, registry=registry)

    assert (m.id in registry.get_persons_in_location(home_id))
    assert (a.id in registry.get_persons_in_location(home_id))
