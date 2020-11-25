# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import List, Optional

import numpy as np

from ..environment import Home, Location, CityRegistry, GroceryStore, Road, Cemetery, Hospital, \
    Office, School, SimTimeTuple, HospitalState, ContactRate, BusinessLocationState, \
    NonEssentialBusinessLocationState, RetailStore, BarberShop, PopulationParams

__all__ = ['make_standard_locations']


def make_standard_locations(population_params: PopulationParams,
                            registry: CityRegistry,
                            numpy_rng: Optional[np.random.RandomState] = None) -> List[Location]:
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()
    location_type_to_params = population_params.location_type_to_params
    req_loc_types = [Hospital, Home, GroceryStore, Office, School]
    for loc_type in req_loc_types:
        assert loc_type in location_type_to_params, f'loc_type - {loc_type} is required for this helper.'

    road = Road(registry, numpy_rng=numpy_rng)

    cemetery = Cemetery(registry, 'cemetery', road_id=road.id, numpy_rng=numpy_rng)

    hospitals: List[Location] = [Hospital(registry=registry,
                                          name=f'hospital_{i}',
                                          road_id=road.id,
                                          init_state=HospitalState(
                                              is_open=True,
                                            #   contact_rate=ContactRate(0, 3, 1, 0.1, 0., 0.),
                                              contact_rate=ContactRate(0, 3, 1, 0.15, 0., 0.),
                                              visitor_capacity=location_type_to_params[Hospital].visitor_capacity,
                                              patient_capacity=location_type_to_params[Hospital].visitor_capacity),
                                          numpy_rng=numpy_rng
                                          ) for i in range(location_type_to_params[Hospital].num)]

    homes: List[Location] = [Home(registry=registry, name=f'house_{i}', road_id=road.id, numpy_rng=numpy_rng)
                             for i in range(location_type_to_params[Home].num)]

    grocery_stores: List[Location] = [GroceryStore(
        registry=registry,
        name=f'grocery_{i}',
        road_id=road.id,
        init_state=BusinessLocationState(
            is_open=True,
            # contact_rate=ContactRate(0, 1, 0, 0.2, 0.25, 0.3),
            contact_rate=ContactRate(0, 1, 0, 0.3, 0.375, 0.45),
            visitor_capacity=location_type_to_params[GroceryStore].visitor_capacity,
            open_time=SimTimeTuple(hours=tuple(range(7, 21)), week_days=tuple(range(0, 6)))),
        numpy_rng=numpy_rng
    ) for i in range(location_type_to_params[GroceryStore].num)]

    offices: List[Location] = [Office(
        registry=registry,
        name=f'offices_{i}',
        road_id=road.id,
        init_state=NonEssentialBusinessLocationState(
            is_open=True,
            # contact_rate=ContactRate(2, 1, 0, 0.1, 0.01, 0.01),
            contact_rate=ContactRate(2, 1, 0, 0.15, 0.015, 0.015),
            visitor_capacity=location_type_to_params[Office].visitor_capacity,
            open_time=SimTimeTuple(hours=tuple(range(9, 17)), week_days=tuple(range(0, 5)))),
        numpy_rng=numpy_rng
    ) for i in range(location_type_to_params[Office].num)]

    schools: List[Location] = [School(
        registry=registry,
        name=f'school_{i}',
        road_id=road.id,
        init_state=NonEssentialBusinessLocationState(
            is_open=True,
            # contact_rate=ContactRate(5, 1, 0, 0.1, 0., 0.1),
            contact_rate=ContactRate(5, 1, 0, 0.15, 0., 0.15),
            visitor_capacity=location_type_to_params[School].visitor_capacity,
            open_time=SimTimeTuple(hours=tuple(range(7, 15)), week_days=tuple(range(0, 5)))),
        numpy_rng=numpy_rng
    ) for i in range(location_type_to_params[School].num)]

    all_locs: List[Location] = homes + grocery_stores + offices + schools + hospitals + [road, cemetery]

    if RetailStore in location_type_to_params:
        all_locs += [RetailStore(
            registry=registry,
            name=f'retail_{i}',
            road_id=road.id,
            init_state=NonEssentialBusinessLocationState(
                is_open=True,
                # contact_rate=ContactRate(0, 1, 0, 0.2, 0.25, 0.3),
                contact_rate=ContactRate(0, 1, 0, 0.3, 0.375, 0.45),
                visitor_capacity=location_type_to_params[RetailStore].visitor_capacity,
                open_time=SimTimeTuple(hours=tuple(range(7, 21)), week_days=tuple(range(0, 6)))),
            numpy_rng=numpy_rng
        ) for i in range(location_type_to_params[RetailStore].num)]

    if BarberShop in location_type_to_params:
        all_locs += [BarberShop(
            registry=registry,
            name=f'barber_{i}',
            road_id=road.id,
            init_state=NonEssentialBusinessLocationState(
                is_open=True,
                # contact_rate=ContactRate(1, 1, 0, 0.5, 0.3, 0.1),
                contact_rate=ContactRate(1, 1, 0, 0.75, 0.45, 0.15),
                visitor_capacity=location_type_to_params[BarberShop].visitor_capacity,
                open_time=SimTimeTuple(hours=tuple(range(9, 17)), week_days=tuple(range(1, 7)))),
            numpy_rng=numpy_rng
        ) for i in range(location_type_to_params[BarberShop].num)]

    return all_locs
