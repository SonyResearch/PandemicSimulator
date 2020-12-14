# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import List, Optional

import numpy as np

from .person_routines import get_minor_routines, get_retired_routines, get_worker_during_work_routines, \
    get_worker_outside_work_routines
from ..environment import Home, CityRegistry, Person, Risk, Minor, School, Worker, Retired, JobCounselor, \
    PopulationParams, SimTimeTuple, Hospital, PersonID, PersonState

__all__ = ['make_us_age_population']

age_group = range(2, 101)


def get_hospital_work_time(numpy_rng: np.random.RandomState) -> SimTimeTuple:
    # this is only for a hospital, roll the dice for day shift or night shift
    if numpy_rng.random() < 0.5:
        # night shift
        hours = (22, 23) + tuple(range(0, 7))
    else:
        # distribute the work hours of the day shifts between 7 am to 10pm
        start = numpy_rng.randint(7, 13)
        hours = tuple(range(start, start + 9))

    start = numpy_rng.randint(0, 2)
    week_days = tuple(range(start, start + 6))
    return SimTimeTuple(hours, week_days)


def get_us_age_distribution(num_persons: int,
                            numpy_rng: Optional[np.random.RandomState] = None) -> List[int]:
    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()
    age_p = np.zeros(100)
    for i, age in enumerate(age_group):
        if age < 60:
            age_p[i] = numpy_rng.normal(1, 0.05)
        else:
            age_p[i] = (1 + (age - 60) * (0.05 - 1) / (100 - 60)) * numpy_rng.normal(1, 0.05)
    age_p /= np.sum(age_p)
    ages = [numpy_rng.choice(np.arange(1, 101), p=age_p) for _ in range(num_persons)]
    print(f'Average age: {np.average(ages)}')
    return ages


def make_us_age_population(population_params: PopulationParams,
                           registry: CityRegistry,
                           regulation_compliance_prob: float = 1.0,
                           numpy_rng: Optional[np.random.RandomState] = None) -> List[Person]:
    home_ids = registry.location_ids_of_type(Home)
    school_ids = registry.location_ids_of_type(School)
    num_persons = population_params.num_persons

    numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

    job_counselor = JobCounselor(population_params, registry, numpy_rng=numpy_rng)

    # assign age (based on the age profile of USA)
    ages = get_us_age_distribution(num_persons, numpy_rng=numpy_rng)
    ages.sort()
    persons: List[Person] = []
    # last 15% of homes in homes_id are for retirees only (1-2 retirees each)
    retired_homes = int((float(len(home_ids))) * 0.15)
    family_homes = len(home_ids) - retired_homes
    age_iter = 0
    # assign minors randomly to family homes
    while ages[age_iter] <= 18:
        age = ages[age_iter]
        home_id = home_ids[numpy_rng.randint(0, family_homes)]
        risk = numpy_rng.choice([Risk.LOW, Risk.HIGH], p=[1 - age / age_group.stop, age / age_group.stop])
        school_id = school_ids[numpy_rng.randint(0, len(school_ids))]
        persons.append(Minor(person_id=PersonID(f'minor_{age_iter}', age),
                             home=home_id,
                             school=school_id,
                             registry=registry,
                             outside_school_routines=get_minor_routines(home_id, age, registry, numpy_rng=numpy_rng),
                             regulation_compliance_prob=regulation_compliance_prob,
                             init_state=PersonState(current_location=home_id, risk=risk),
                             numpy_rng=numpy_rng))
        age_iter += 1
    home_iter = 0
    # assign adults to family homes, each family home must have at least one adult
    while home_iter < family_homes:
        home_id = home_ids[home_iter]
        num_adults = numpy_rng.randint(1, 2)
        if ages[age_iter] > 65:
            break
        for i in range(num_adults):
            age = ages[age_iter]
            if age > 65:
                break
            risk = numpy_rng.choice([Risk.LOW, Risk.HIGH], p=[1 - age / age_group.stop, age / age_group.stop])
            work_id = job_counselor.next_available_work_id()
            assert work_id is not None, 'Not enough available jobs, increase assignee capacity of certain businesses'

            if work_id in registry.location_ids_of_type(Hospital):
                work_time = get_hospital_work_time(numpy_rng)
            else:
                work_time = registry.get_location_open_time(work_id)

            persons.append(Worker(person_id=PersonID(f'worker_{age_iter}', age),
                                  home=home_id,
                                  work=work_id,
                                  registry=registry,
                                  work_time=work_time,
                                  outside_work_routines=get_worker_outside_work_routines(home_id, registry,
                                                                                         numpy_rng=numpy_rng),
                                  during_work_routines=get_worker_during_work_routines(work_id, registry, numpy_rng),
                                  regulation_compliance_prob=regulation_compliance_prob,
                                  init_state=PersonState(current_location=home_id, risk=risk),
                                  numpy_rng=numpy_rng))

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
        num_retirees = numpy_rng.randint(1, 3)
        for i in range(num_retirees):
            age = ages[age_iter]
            risk = numpy_rng.choice([Risk.LOW, Risk.HIGH], p=[1 - age / age_group.stop, age / age_group.stop])
            persons.append(Retired(person_id=PersonID(f'retired_{age_iter}', age),
                                   home=home_id,
                                   registry=registry,
                                   routines=get_retired_routines(home_id, registry, numpy_rng=numpy_rng),
                                   regulation_compliance_prob=regulation_compliance_prob,
                                   init_state=PersonState(current_location=home_id, risk=risk),
                                   numpy_rng=numpy_rng))
            age_iter += 1
        home_iter += 1
    home_iter = 0
    # assign remaining retirees to family homes
    while age_iter < len(ages):
        home_id = home_ids[home_iter]
        num_retirees = numpy_rng.randint(1, 2)
        for i in range(num_retirees):
            age = ages[age_iter]
            risk = numpy_rng.choice([Risk.LOW, Risk.HIGH], p=[1 - age / age_group.stop, age / age_group.stop])
            persons.append(Retired(person_id=PersonID(f'retired_{age_iter}', age),
                                   home=home_id,
                                   registry=registry,
                                   routines=get_retired_routines(home_id, registry, numpy_rng=numpy_rng),
                                   regulation_compliance_prob=regulation_compliance_prob,
                                   init_state=PersonState(current_location=home_id, risk=risk),
                                   numpy_rng=numpy_rng))
            age_iter += 1
        home_iter += 1
        if home_iter >= len(home_ids):
            home_iter = 0
    return persons
