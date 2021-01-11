# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from typing import List, cast
from uuid import uuid4

import numpy as np

from .interfaces import globals, Risk, Person, PersonID, PersonState
from .job_counselor import JobCounselor
from .location import Home, School, BusinessBaseLocation
from .person import Retired, Worker, Minor
from .simulator_config import PandemicSimConfig
from ..utils import cluster_into_random_sized_groups

__all__ = ['make_population']

age_group = range(2, 101)


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


def infection_risk(age: int) -> Risk:
    return cast(Risk,
                globals.numpy_rng.choice([Risk.LOW, Risk.HIGH], p=[1 - age / age_group.stop, age / age_group.stop]))


def make_population(sim_config: PandemicSimConfig) -> List[Person]:
    """
    Creates a realistic us-age distributed population with home assignment and returns a list of persons.

    The overview of home assignment is as follows:

    a) "Only 4.5 percent of older adults live in nursing homes and
    2 percent in assisted living facilities. The majority of older adults (93.5 percent) live in the community."
    - https://www.ncbi.nlm.nih.gov/books/NBK51841/

    Select 6.5% of older adults (age > 65) and cluster them as groups of 1 or 2 and assign each
    group to a nursing home. Distribute the remaining older adults randomly across the non-nursing homes

    b) "In 2019, there was an average of 1.93 children under 18 per family in the United States"
    - https://www.statista.com/statistics/718084/average-number-of-own-children-per-family/

    Cluster minors into 1-3 sized uniform groups and assign each group to a home

    c) Assign one adult to each minor-included homes and then distribute the remaining
    uniformly across all non-nursing homes

    :param sim_config: PandemicSimConfig instance
    :return: a list of person instances
    """
    assert globals.registry, 'No registry found. Create the repo wide registry first by calling init_globals()'
    registry = globals.registry
    numpy_rng = globals.numpy_rng

    persons: List[Person] = []

    # ages based on the age profile of USA
    ages = get_us_age_distribution(sim_config.num_persons)
    numpy_rng.shuffle(ages)
    minor_ages = []
    adults_ages = []
    old_adults_ages = []
    for age in ages:
        if age <= 18:
            minor_ages.append(age)
        elif 18 < age <= 65:
            adults_ages.append(age)
        else:
            old_adults_ages.append(age)

    # a) Select 6.5% of older adults (age > 65) and cluster them as groups of 1 or 2 and assign each
    # group to a nursing home. Distribute the remaining older adults randomly across the non-nursing homes
    all_homes = list(registry.location_ids_of_type(Home))
    numpy_rng.shuffle(all_homes)
    num_adults_in_nursing = np.ceil(len(old_adults_ages) * 0.065).astype('int')
    old_adults_in_nursing_ages = old_adults_ages[:num_adults_in_nursing]
    old_adults_not_in_nursing_ages = old_adults_ages[num_adults_in_nursing:]
    clustered_old_adults_in_nursing_ages = cluster_into_random_sized_groups(old_adults_in_nursing_ages, 1, 2, numpy_rng)
    homes_ages = [(all_homes[_i], _a) for _i, _g in enumerate(clustered_old_adults_in_nursing_ages) for _a in _g]
    non_nursing_homes = all_homes[len(clustered_old_adults_in_nursing_ages):]
    homes_ages.extend([(numpy_rng.choice(non_nursing_homes), _a) for _a in old_adults_not_in_nursing_ages])
    for home, age in homes_ages:
        persons.append(Retired(person_id=PersonID(f'retired_{str(uuid4())}', age),
                               home=home,
                               regulation_compliance_prob=sim_config.regulation_compliance_prob,
                               init_state=PersonState(current_location=home, risk=infection_risk(age))))

    # b) Cluster minors into 1-3 sized uniform groups and assign each group to a home
    minor_homes = []
    schools = registry.location_ids_of_type(School)
    clustered_minor_ages = cluster_into_random_sized_groups(minor_ages, 1, 3, numpy_rng)
    for g in clustered_minor_ages:
        home = all_homes.pop(0)
        minor_homes.append(home)
        for age in g:
            persons.append(Minor(person_id=PersonID(f'minor_{str(uuid4())}', age),
                                 home=home,
                                 school=numpy_rng.choice(schools) if len(schools) > 0 else None,
                                 regulation_compliance_prob=sim_config.regulation_compliance_prob,
                                 init_state=PersonState(current_location=home, risk=infection_risk(age))))

    # c) Assign one adult to each minor-included homes and then distribute the remaining uniformly across
    # all non-nursing homes
    work_ids = registry.location_ids_of_type(BusinessBaseLocation)
    job_counselor = JobCounselor(sim_config.location_configs)
    assert len(adults_ages) > 0 and len(work_ids) > 0, 'no business locations found!'
    for age in adults_ages:
        home = minor_homes.pop(0) if len(minor_homes) > 0 else numpy_rng.choice(non_nursing_homes)
        work_package = job_counselor.next_available_work()
        assert work_package, 'Not enough available jobs, increase the capacity of certain businesses'
        persons.append(Worker(person_id=PersonID(f'worker_{str(uuid4())}', age),
                              home=home,
                              work=work_package.work,
                              work_time=work_package.work_time,
                              regulation_compliance_prob=sim_config.regulation_compliance_prob,
                              init_state=PersonState(current_location=home, risk=infection_risk(age))))

    return persons
