# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

import pytest

from pandemic_simulator.environment import Office, GroceryStore, CityRegistry, BusinessLocationState, \
    NonEssentialBusinessLocationState, BusinessBaseLocation, PopulationParams, LocationParams, JobCounselor


@pytest.fixture
def population_params():
    return PopulationParams(num_persons=10,
                            location_type_to_params={Office: LocationParams(2, 5), GroceryStore: LocationParams(1, 3)})


def city_registry(params):
    registry = CityRegistry()
    location_type_to_params = params.location_type_to_params
    _ = [GroceryStore(
        name=f'grocery_{i}',
        registry=registry,
        init_state=BusinessLocationState(is_open=True,
                                         visitor_capacity=location_type_to_params[GroceryStore].visitor_capacity)
    ) for i in range(location_type_to_params[GroceryStore].num)]

    _ = [Office(
        name=f'office_{i}',
        registry=registry,
        init_state=NonEssentialBusinessLocationState(is_open=True,
                                                     visitor_capacity=location_type_to_params[Office].visitor_capacity)
    ) for i in range(location_type_to_params[Office].num)]

    return registry


def test_job_counselor(population_params):
    registry = city_registry(population_params)
    job_counselor = JobCounselor(population_params, registry)

    all_work_ids = registry.location_ids_of_type(BusinessBaseLocation)
    total_jobs = sum([loc_params.num * loc_params.worker_capacity
                      for loc_params in population_params.location_type_to_params.values()])

    for _ in range(total_jobs):
        work_id = job_counselor.next_available_work_id()
        assert work_id in all_work_ids

    # should return None when asked for next available work id since all are taken
    assert job_counselor.next_available_work_id() is None
