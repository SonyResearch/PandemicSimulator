# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from typing import Sequence, Type, Optional

import numpy as np

from ..environment import LocationID, PersonRoutine, Registry, SimTimeInterval, GroceryStore, \
    RetailStore, BarberShop, Retired, Restaurant, Bar

__all__ = ['get_minor_routines', 'get_adult_routines']

# helper method that encapsulates adding restaurant routine 
def add_restaurant_routine(routines,
                    registry: Registry,
                    numpy_rng: Optional[np.random.RandomState] = None):
    restaurants = registry.location_ids_of_type(Restaurant)
    if len(restaurants) > 0:
        interval_in_days = 1
        routines.append(PersonRoutine(start_loc=None,
                                      end_loc=restaurants[numpy_rng.randint(0, len(restaurants))],
                                      trigger_interval=SimTimeInterval(day=interval_in_days,
                                                                       offset_day=numpy_rng.randint(0,
                                                                                                    interval_in_days))
                                      )
                        )

# helper method that encapsulates adding bar routine 
def add_bar_routine(routines,
            registry: Registry,
            numpy_rng: Optional[np.random.RandomState] = None):
    bars = registry.location_ids_of_type(Bar)
    if len(bars) > 0:
        interval_in_days = 4
        routines.append(PersonRoutine(start_loc=None,
                                      end_loc=bars[numpy_rng.randint(0, len(bars))],
                                      trigger_interval=SimTimeInterval(day=interval_in_days,
                                                                       offset_day=numpy_rng.randint(0,
                                                                                                    interval_in_days)),
                                      end_locs=bars,
                                      explore_probability=0.03
                                      )

                        )

def get_minor_routines(home_id: LocationID,
                       registry: Registry,
                       numpy_rng: Optional[np.random.RandomState] = None) -> Sequence[PersonRoutine]:
    routines = []
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

    barber_shops = registry.location_ids_of_type(BarberShop)
    if len(barber_shops) > 0:
        routines.append(PersonRoutine(start_loc=home_id,
                                      end_loc=barber_shops[numpy_rng.randint(0, len(barber_shops))],
                                      trigger_interval=SimTimeInterval(day=30)))

    # add restaurant routine
    add_restaurants(routines, registry, numpy_rng)

    return routines


def get_adult_routines(person_type: Type,
                       home_id: LocationID,
                       registry: Registry,
                       numpy_rng: Optional[np.random.RandomState] = None) -> Sequence[PersonRoutine]:
    routines = []
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

    shopping_rate = 1 if isinstance(person_type, Retired) else 1
    grocery_stores = registry.location_ids_of_type(GroceryStore)
    if len(grocery_stores) > 0:
        interval_in_days = int(7 / shopping_rate)
        routines.append(PersonRoutine(start_loc=None,
                                      end_loc=grocery_stores[numpy_rng.randint(0, len(grocery_stores))],
                                      trigger_interval=SimTimeInterval(day=interval_in_days,
                                                                       offset_day=numpy_rng.randint(0,
                                                                                                    interval_in_days)),
                                      end_locs=grocery_stores,
                                      explore_probability=0.05))

    retail_stores = registry.location_ids_of_type(RetailStore)
    if len(retail_stores) > 0:
        interval_in_days = int(7 / shopping_rate)
        routines.append(PersonRoutine(start_loc=None,
                                      end_loc=retail_stores[numpy_rng.randint(0, len(retail_stores))],
                                      trigger_interval=SimTimeInterval(day=interval_in_days,
                                                                       offset_day=numpy_rng.randint(0,
                                                                                                    interval_in_days)),
                                      end_locs=retail_stores,
                                      explore_probability=0.05))

    barber_shops = registry.location_ids_of_type(BarberShop)
    if len(barber_shops) > 0:
        interval_in_days = 30
        routines.append(PersonRoutine(start_loc=home_id,
                                      end_loc=barber_shops[numpy_rng.randint(0, len(barber_shops))],
                                      trigger_interval=SimTimeInterval(day=interval_in_days,
                                                                       offset_day=numpy_rng.randint(0,
                                                                                                    interval_in_days))
                                      )
                        )

    add_bar_routine(routines, registry, numpy_rng)

    return routines

def get_during_work_routines(registry: Registry):
    routines = []
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

    add_restaurant_routine(routines, registry, numpy_rng)

    return routines