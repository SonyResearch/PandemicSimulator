# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from ..environment import Home, GroceryStore, Office, School, Hospital, RetailStore, HairSalon, Restaurant, \
    LocationParams, PopulationParams, Bar

__all__ = ['town_population_params', 'small_town_population_params', 'test_population_params',
           'tiny_town_population_params', 'medium_town_population_params',
           'above_medium_town_population_params']

town_population_params = PopulationParams(
    num_persons=10000,
    location_type_to_params={
        Home: LocationParams(num=3000),
        GroceryStore: LocationParams(num=10, worker_capacity=10, visitor_capacity=30),
        Office: LocationParams(num=50, worker_capacity=200, visitor_capacity=0),
        School: LocationParams(num=3, worker_capacity=40, visitor_capacity=300),
        Hospital: LocationParams(num=1, worker_capacity=80, visitor_capacity=100),
        RetailStore: LocationParams(num=15, worker_capacity=10, visitor_capacity=30),
        HairSalon: LocationParams(num=20, worker_capacity=3, visitor_capacity=5),
        Restaurant: LocationParams(num=20, worker_capacity=6, visitor_capacity=30),
        Bar: LocationParams(num=10, worker_capacity=8, visitor_capacity=30),
    },
    viz_scale=2)

above_medium_town_population_params = PopulationParams(
    num_persons=4000,
    location_type_to_params={
        Home: LocationParams(num=1200),
        GroceryStore: LocationParams(num=16, worker_capacity=5, visitor_capacity=30),
        Office: LocationParams(num=20, worker_capacity=200, visitor_capacity=0),
        School: LocationParams(num=4, worker_capacity=40, visitor_capacity=300),
        Hospital: LocationParams(num=4, worker_capacity=30, visitor_capacity=10),
        RetailStore: LocationParams(num=16, worker_capacity=5, visitor_capacity=30),
        HairSalon: LocationParams(num=16, worker_capacity=3, visitor_capacity=5),
        Restaurant: LocationParams(num=8, worker_capacity=6, visitor_capacity=30),
        Bar: LocationParams(num=8, worker_capacity=4, visitor_capacity=30),
    },
    viz_scale=3)

medium_town_population_params = PopulationParams(
    num_persons=2000,
    location_type_to_params={
        Home: LocationParams(num=600),
        GroceryStore: LocationParams(num=8, worker_capacity=5, visitor_capacity=30),
        Office: LocationParams(num=10, worker_capacity=200, visitor_capacity=0),
        School: LocationParams(num=2, worker_capacity=40, visitor_capacity=300),
        Hospital: LocationParams(num=2, worker_capacity=30, visitor_capacity=10),
        RetailStore: LocationParams(num=8, worker_capacity=5, visitor_capacity=30),
        HairSalon: LocationParams(num=8, worker_capacity=3, visitor_capacity=5),
        Restaurant: LocationParams(num=4, worker_capacity=6, visitor_capacity=30),
        Bar: LocationParams(num=4, worker_capacity=3, visitor_capacity=30),
    },
    viz_scale=3)

small_town_population_params = PopulationParams(
    num_persons=1000,
    location_type_to_params={
        Home: LocationParams(num=300),
        GroceryStore: LocationParams(num=4, worker_capacity=5, visitor_capacity=30),
        Office: LocationParams(num=5, worker_capacity=200, visitor_capacity=0),
        School: LocationParams(num=1, worker_capacity=40, visitor_capacity=300),
        Hospital: LocationParams(num=1, worker_capacity=30, visitor_capacity=10),
        RetailStore: LocationParams(num=4, worker_capacity=5, visitor_capacity=30),
        HairSalon: LocationParams(num=4, worker_capacity=3, visitor_capacity=5),
        Restaurant: LocationParams(num=2, worker_capacity=6, visitor_capacity=30),
        Bar: LocationParams(num=2, worker_capacity=5, visitor_capacity=30),
    },
    viz_scale=3)

tiny_town_population_params = PopulationParams(
    num_persons=500,
    location_type_to_params={
        Home: LocationParams(num=150),
        GroceryStore: LocationParams(num=2, worker_capacity=5, visitor_capacity=30),
        Office: LocationParams(num=2, worker_capacity=200, visitor_capacity=0),
        School: LocationParams(num=1, worker_capacity=20, visitor_capacity=300),
        Hospital: LocationParams(num=1, worker_capacity=15, visitor_capacity=5),
        RetailStore: LocationParams(num=2, worker_capacity=5, visitor_capacity=30),
        HairSalon: LocationParams(num=2, worker_capacity=3, visitor_capacity=5),
        Restaurant: LocationParams(num=1, worker_capacity=6, visitor_capacity=30),
        Bar: LocationParams(num=1, worker_capacity=3, visitor_capacity=30),
    },
    viz_scale=3)

test_population_params = PopulationParams(
    num_persons=100,
    location_type_to_params={
        Home: LocationParams(num=30),
        GroceryStore: LocationParams(num=1, worker_capacity=5, visitor_capacity=30),
        Office: LocationParams(num=1, worker_capacity=200, visitor_capacity=0),
        School: LocationParams(num=1, worker_capacity=40, visitor_capacity=300),
        Hospital: LocationParams(num=1, worker_capacity=30, visitor_capacity=2),
        Restaurant: LocationParams(num=1, worker_capacity=3, visitor_capacity=10),
        Bar: LocationParams(num=1, worker_capacity=3, visitor_capacity=10),
    },
    viz_scale=4)
