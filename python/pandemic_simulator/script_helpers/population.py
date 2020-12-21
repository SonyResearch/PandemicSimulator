# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import List, Optional

import numpy as np

from .person_routines import get_minor_routines, get_retired_routines, get_worker_during_work_routines, \
    get_worker_outside_work_routines
from ..environment import Home, Person, Risk, Minor, School, Worker, Retired, JobCounselor, \
    SimTimeTuple, Hospital, PersonID, PersonState, globals, BusinessBaseLocation, LocationID

__all__ = ['make_population']

age_group = range(2, 101)


def get_hospital_work_time() -> SimTimeTuple:
    # this is only for a hospital, roll the dice for day shift or night shift
    if globals.numpy_rng.random() < 0.5:
        # night shift
        hours = (22, 23) + tuple(range(0, 7))
    else:
        # distribute the work hours of the day shifts between 7 am to 10pm
        start = globals.numpy_rng.randint(7, 13)
        hours = tuple(range(start, start + 9))

    start = globals.numpy_rng.randint(0, 2)
    week_days = tuple(range(start, start + 6))
    return SimTimeTuple(hours, week_days)


def get_us_age_distribution(num_persons: int) -> List[int]:
    age_p = np.zeros(100)
    for i, age in enumerate(age_group):
        if age < 60:
            age_p[i] = globals.numpy_rng.normal(1, 0.05)
        else:
            age_p[i] = (1 + (age - 60) * (0.05 - 1) / (100 - 60)) * globals.numpy_rng.normal(1, 0.05)
    age_p /= np.sum(age_p)
    ages = [globals.numpy_rng.choice(np.arange(1, 101), p=age_p) for _ in range(num_persons)]
    print(f'Average age: {np.average(ages)}')
    return ages


def make_population(num_persons: int,
                    regulation_compliance_prob: float = 1.0,
                    job_counselor: Optional[JobCounselor] = None) -> List[Person]:
    assert globals.registry, 'No registry found. Create the repo wide registry first by calling init_globals()'

    home_ids = globals.registry.location_ids_of_type(Home)
    school_ids = globals.registry.location_ids_of_type(School)

    # assign age (based on the age profile of USA)
    ages = get_us_age_distribution(num_persons)
    ages.sort()
    persons: List[Person] = []
    # last 15% of homes in homes_id are for retirees only (1-2 retirees each)
    retired_homes = int((float(len(home_ids))) * 0.15)
    family_homes = len(home_ids) - retired_homes
    age_iter = 0
    # assign minors randomly to family homes
    while ages[age_iter] <= 18:
        age = ages[age_iter]
        home_id = home_ids[globals.numpy_rng.randint(0, family_homes)]
        risk = globals.numpy_rng.choice([Risk.LOW, Risk.HIGH], p=[1 - age / age_group.stop, age / age_group.stop])
        school_id = school_ids[globals.numpy_rng.randint(0, len(school_ids))]
        persons.append(Minor(person_id=PersonID(f'minor_{age_iter}', age),
                             home=home_id,
                             school=school_id,
                             outside_school_routines=get_minor_routines(home_id, age),
                             regulation_compliance_prob=regulation_compliance_prob,
                             init_state=PersonState(current_location=home_id, risk=risk)))
        age_iter += 1
    home_iter = 0
    # assign adults to family homes, each family home must have at least one adult
    while home_iter < family_homes:
        home_id = home_ids[home_iter]
        num_adults = globals.numpy_rng.randint(1, 2)
        if ages[age_iter] > 65:
            break
        for i in range(num_adults):
            age = ages[age_iter]
            if age > 65:
                break
            risk = globals.numpy_rng.choice([Risk.LOW, Risk.HIGH], p=[1 - age / age_group.stop, age / age_group.stop])
            if job_counselor is not None:
                available_work_id = job_counselor.next_available_work_id()
                assert available_work_id, 'Not enough available jobs, increase capacity of certain businesses'
                work_id: LocationID = available_work_id
            else:
                work_ids = globals.registry.location_ids_of_type(BusinessBaseLocation)
                work_id = work_ids[globals.numpy_rng.randint(0, len(work_ids))]

            if work_id in globals.registry.location_ids_of_type(Hospital):
                work_time: Optional[SimTimeTuple] = get_hospital_work_time()
            else:
                work_time = globals.registry.get_location_open_time(work_id)

            persons.append(Worker(person_id=PersonID(f'worker_{age_iter}', age),
                                  home=home_id,
                                  work=work_id,
                                  work_time=work_time,
                                  outside_work_routines=get_worker_outside_work_routines(home_id),
                                  during_work_routines=get_worker_during_work_routines(work_id),
                                  regulation_compliance_prob=regulation_compliance_prob,
                                  init_state=PersonState(current_location=home_id, risk=risk)))

            age_iter += 1
        home_iter += 1
        # if there are remaining adults to be assigned, but all family homes have at least one adult already,
        # loop back to beginning of home_ids
        if ages[age_iter] <= 65 and home_iter >= family_homes:
            home_iter = 0
    home_iter = family_homes
    # fill retiree homes
    while family_homes < home_iter < len(home_ids):
        home_id = home_ids[home_iter]
        num_retirees = globals.numpy_rng.randint(1, 3)
        for i in range(num_retirees):
            age = ages[age_iter]
            risk = globals.numpy_rng.choice([Risk.LOW, Risk.HIGH], p=[1 - age / age_group.stop, age / age_group.stop])
            persons.append(Retired(person_id=PersonID(f'retired_{age_iter}', age),
                                   home=home_id,
                                   routines=get_retired_routines(home_id),
                                   regulation_compliance_prob=regulation_compliance_prob,
                                   init_state=PersonState(current_location=home_id, risk=risk)))
            age_iter += 1
        home_iter += 1
    home_iter = 0
    # assign remaining retirees to family homes
    while age_iter < len(ages):
        home_id = home_ids[home_iter]
        num_retirees = globals.numpy_rng.randint(1, 2)
        for i in range(num_retirees):
            age = ages[age_iter]
            risk = globals.numpy_rng.choice([Risk.LOW, Risk.HIGH], p=[1 - age / age_group.stop, age / age_group.stop])
            persons.append(Retired(person_id=PersonID(f'retired_{age_iter}', age),
                                   home=home_id,
                                   routines=get_retired_routines(home_id),
                                   regulation_compliance_prob=regulation_compliance_prob,
                                   init_state=PersonState(current_location=home_id, risk=risk)))
            age_iter += 1
        home_iter += 1
        if home_iter >= len(home_ids):
            home_iter = 0
    return persons
