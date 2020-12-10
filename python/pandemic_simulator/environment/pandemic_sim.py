# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from collections import defaultdict, deque
from typing import DefaultDict, Dict, List, Optional, Sequence, cast
from functools import lru_cache

import numpy as np

from .interfaces import ContactRate, ContactTracer, PandemicRegulation, PandemicSimState, PandemicTesting, \
    PandemicTestResult, \
    DEFAULT, GlobalTestingState, InfectionModel, InfectionSummary, Location, LocationID, Person, PersonID, Registry, \
    SimTime, SimTimeInterval, sorted_infection_summary
from .location import Hospital

__all__ = ['PandemicSim']


class PandemicSim:
    """Class that implements the pandemic simulator."""

    _id_to_person: Dict[PersonID, Person]
    _id_to_location: Dict[LocationID, Location]
    _infection_model: InfectionModel
    _pandemic_testing: PandemicTesting
    _registry: Registry
    _contact_tracer: Optional[ContactTracer]
    _new_time_slot_interval: SimTimeInterval
    _infection_update_interval: SimTimeInterval
    _infection_threshold: int
    _numpy_rng: np.random.RandomState

    _type_to_locations: DefaultDict
    _hospital_ids: List[LocationID]
    _state: PandemicSimState

    def __init__(self,
                 persons: Sequence[Person],
                 locations: Sequence[Location],
                 infection_model: InfectionModel,
                 pandemic_testing: PandemicTesting,
                 registry: Registry,
                 contact_tracer: Optional[ContactTracer] = None,
                 new_time_slot_interval: SimTimeInterval = SimTimeInterval(day=1),
                 infection_update_interval: SimTimeInterval = SimTimeInterval(day=1),
                 infection_threshold: int = 0,
                 numpy_rng: Optional[np.random.RandomState] = None):
        """
        :param persons: A sequence of Person instances.
        :param locations: A sequence of Location instances.
        :param infection_model: Infection model instance.
        :param pandemic_testing: PandemicTesting instance.
        :param registry: Registry instance.
        :param contact_tracer: Optional ContactTracer instance.
        :param new_time_slot_interval: interval for updating contact tracer if that is not None. Default is set daily.
        :param infection_update_interval: interval for updating infection states. Default is set once daily.
        :param infection_threshold: If the infection summary is greater than the specified threshold, a
            boolean in PandemicSimState is set to True.
        :param numpy_rng: Random number generator.
        """
        self._id_to_person = {p.id: p for p in persons}
        self._id_to_location = {loc.id: loc for loc in locations}
        self._infection_model = infection_model
        self._pandemic_testing = pandemic_testing
        self._registry = registry
        self._contact_tracer = contact_tracer
        self._new_time_slot_interval = new_time_slot_interval
        self._infection_update_interval = infection_update_interval
        self._infection_threshold = infection_threshold
        self._numpy_rng = numpy_rng if numpy_rng is not None else np.random.RandomState()

        self._type_to_locations = defaultdict(list)
        for loc in locations:
            self._type_to_locations[type(loc)].append(loc)
        self._hospital_ids = [loc.id for loc in locations if isinstance(loc, Hospital)]

        num_persons = len(persons)

        self._state = PandemicSimState(
            id_to_person_state={person.id: person.state for person in persons},
            id_to_location_state={location.id: location.state for location in locations},
            global_infection_summary={s: 0 for s in sorted_infection_summary},
            global_testing_state=GlobalTestingState(summary={s: num_persons if s == InfectionSummary.NONE else 0
                                                             for s in sorted_infection_summary},
                                                    num_tests=0),
            sim_time=SimTime(),
            regulation_stage=0,
            infection_above_threshold=False
        )

    def _compute_contacts(self, location: Location) -> dict:
        assignees = location.state.assignees_in_location
        visitors = location.state.visitors_in_location
        cr = location.state.contact_rate

        groups = [(assignees, assignees),
                  (assignees, visitors),
                  (visitors, visitors)]
        constraints = [(cr.min_assignees, cr.fraction_assignees),
                       (cr.min_assignees_visitors, cr.fraction_assignees_visitors),
                       (cr.min_visitors, cr.fraction_visitors)]

        contacts_x: List = list()
        contacts_y: List = list()
        for grp, cst in zip(groups, constraints):
            grp1, grp2 = grp
            minimum, fraction = cst

            possible_contacts_x = []
            possible_contacts_y = []
            num_possible_contacts = 0

            num_possible_contacts = nCk(len(grp1), 2) if grp1 == grp2 else len(grp1) * len(grp2)

            if num_possible_contacts == 0:
                continue

            fraction_sample = min(1., max(0., self._numpy_rng.normal(fraction, 1e-2)))
            real_fraction = max(minimum, int(fraction_sample * num_possible_contacts))
            # we are using an orderedset, it's repeatable
            contact_idx = self._numpy_rng.randint(0, num_possible_contacts, real_fraction)

            if grp1 == grp2:
                possible_contacts_x, possible_contacts_y = comb2_reduced(np.asarray(grp1), contact_idx)
            else:
                possible_contacts_x, possible_contacts_y = prod_reduced(np.asarray(grp1), np.asarray(grp2), contact_idx)
            contacts_x = np.concatenate((contacts_x, possible_contacts_x))
            contacts_y = np.concatenate((contacts_y, possible_contacts_y))

        # Stuff the contact pairs into a dictionary/Set, removing duplicates from repeats in contact_idx
        r = dict()
        for i, c in enumerate(contacts_x):
            r[contacts_x[i], contacts_y[i]] = 0
        return r

    def _compute_infection_probabilities(self, contacts: dict) -> None:
        if len(contacts) < 1:
            return
        infectious_states = {InfectionSummary.INFECTED, InfectionSummary.CRITICAL}

        for c in contacts:
            id_person1 = c[0]
            id_person2 = c[1]
            person1_state = self._id_to_person[id_person1].state
            person2_state = self._id_to_person[id_person2].state
            person1_inf_state = person1_state.infection_state
            person2_inf_state = person2_state.infection_state

            if (
                    # both are not infectious
                    (person1_inf_state is None and person2_inf_state is None) or

                    # both are already infected
                    (person1_inf_state is not None and person2_inf_state is not None and

                     person1_inf_state.summary in infectious_states and person2_inf_state.summary in infectious_states)
            ):
                continue
            elif person1_inf_state is not None and person1_inf_state.summary in infectious_states:
                spread_probability = (person1_inf_state.spread_probability *
                                      person1_state.infection_spread_multiplier)
                person2_state.not_infection_probability *= 1 - spread_probability
            elif person2_inf_state is not None and person2_inf_state.summary in infectious_states:
                spread_probability = (person2_inf_state.spread_probability *
                                      person2_state.infection_spread_multiplier)
                person1_state.not_infection_probability *= 1 - spread_probability

    def _update_global_testing_state(self, new_result: PandemicTestResult, prev_result: PandemicTestResult) -> None:
        if new_result == prev_result:
            # nothing to update
            return

            # person died - just update the test summary and __not__ the num_tests
        if new_result == PandemicTestResult.DEAD and prev_result != PandemicTestResult.DEAD:
            prv = InfectionSummary.CRITICAL if prev_result == PandemicTestResult.CRITICAL else \
                InfectionSummary.INFECTED if prev_result == PandemicTestResult.POSITIVE else InfectionSummary.NONE
            self._state.global_testing_state.summary[InfectionSummary.DEAD] += 1
            self._state.global_testing_state.summary[prv] -= 1

        # person tested positive/critical
        elif (new_result in {PandemicTestResult.POSITIVE, PandemicTestResult.CRITICAL} and
              prev_result in {PandemicTestResult.POSITIVE, PandemicTestResult.NEGATIVE, PandemicTestResult.UNTESTED}):
            new = InfectionSummary.CRITICAL if new_result == PandemicTestResult.CRITICAL else InfectionSummary.INFECTED
            prv = InfectionSummary.INFECTED if prev_result == PandemicTestResult.POSITIVE else InfectionSummary.NONE
            self._state.global_testing_state.summary[new] += 1
            self._state.global_testing_state.summary[prv] -= 1
            self._state.global_testing_state.num_tests += 1  # update number of tests

        # person tested negative after having tested as infected before
        elif (new_result == PandemicTestResult.NEGATIVE and
              prev_result in {PandemicTestResult.POSITIVE, PandemicTestResult.CRITICAL}):
            prv = InfectionSummary.CRITICAL if prev_result == PandemicTestResult.CRITICAL else InfectionSummary.INFECTED
            self._state.global_testing_state.summary[InfectionSummary.RECOVERED] += 1
            self._state.global_testing_state.summary[prv] -= 1
            self._state.global_testing_state.num_tests += 1  # update number of tests

    def step(self) -> None:
        """Method that advances one step through the simulator"""
        # sync all locations
        for location in self._id_to_location.values():
            location.sync(self._state.sim_time)
        self._registry.update_location_specific_information()

        # call person steps
        deque([self.person_update(p) for p in self._id_to_person.values()])

        # update person contacts
        for location in self._id_to_location.values():
            contacts = self._compute_contacts(location)
            if self._contact_tracer:
                self._contact_tracer.add_contacts(contacts)

            self._compute_infection_probabilities(contacts)

        # call infection model steps
        if self._infection_update_interval.trigger_at_interval(self._state.sim_time):
            global_infection_summary = {s: 0 for s in sorted_infection_summary}
            for person in self._id_to_person.values():
                # infection model step
                person.state.infection_state = self._infection_model.step(person.state.infection_state,
                                                                          person.id.age,
                                                                          person.state.risk,
                                                                          1 - person.state.not_infection_probability)

                global_infection_summary[person.state.infection_state.summary] += 1
                person.state.not_infection_probability = 1.

                # test the person for infection
                if self._pandemic_testing.admit_person(person.state):
                    new_test_result = self._pandemic_testing.test_person(person.state)
                    self._update_global_testing_state(new_test_result, person.state.test_result)
                    person.state.test_result = new_test_result

            self._state.global_infection_summary = global_infection_summary
        self._state.infection_above_threshold = (self._state.global_testing_state.summary[InfectionSummary.INFECTED]
                                                 >= self._infection_threshold)

        if self._contact_tracer and self._new_time_slot_interval.trigger_at_interval(self._state.sim_time):
            self._contact_tracer.new_time_slot()

        # call sim time step
        self._state.sim_time.step()

    @staticmethod
    def _get_cr_from_social_distancing(location: Location,
                                       social_distancing: float) -> ContactRate:
        new_fraction = 1 - social_distancing
        cr = location.state.contact_rate
        init_cr = location.init_state.contact_rate
        new_cr = ContactRate(cr.min_assignees,
                             cr.min_assignees_visitors,
                             cr.min_visitors,
                             new_fraction * init_cr.fraction_assignees,
                             new_fraction * init_cr.fraction_assignees_visitors,
                             new_fraction * init_cr.fraction_visitors)

        return new_cr

    def execute_regulation(self, regulation: PandemicRegulation) -> None:
        """
        Receive a regulation that updates the simulator dynamics

        :param regulation: a PandemicRegulation instance
        """

        # update location rules
        sd = regulation.social_distancing
        loc_type_rk = regulation.location_type_to_rule_kwargs

        for loc_type, locations in self._type_to_locations.items():
            rule_kwargs = {}
            if loc_type_rk is not None and loc_type in loc_type_rk:
                rule_kwargs.update(loc_type_rk[loc_type])

            if sd is not None:
                # cr is the same for all locations of a given type. So just use one location to compute the new cr.
                cr = (DEFAULT if sd == DEFAULT
                      else self._get_cr_from_social_distancing(locations[0], cast(float, sd)))
                rule_kwargs.update(dict(contact_rate=cr))

            for loc in locations:
                loc.update_rules(loc.location_rule_type(**rule_kwargs))

        # update person policy
        for person in self._id_to_person.values():
            person.receive_regulation(regulation)

        self._state.regulation_stage = regulation.stage

    @property
    def state(self) -> PandemicSimState:
        """
        Property that returns the current state of the simulator.

        :return: Current state of the simulator.
        """

        return self._state

    def reset(self) -> None:
        for location in self._id_to_location.values():
            location.reset()
        for person in self._id_to_person.values():
            person.reset()

        self._infection_model.reset()
        num_persons = len(self._id_to_person)

        self._state = PandemicSimState(
            id_to_person_state={person_id: person.state for person_id, person in self._id_to_person.items()},
            id_to_location_state={loc_id: loc.state for loc_id, loc in self._id_to_location.items()},
            global_infection_summary={s: 0 for s in sorted_infection_summary},
            global_testing_state=GlobalTestingState(summary={s: num_persons if s == InfectionSummary.NONE else 0
                                                             for s in sorted_infection_summary},
                                                    num_tests=0),
            sim_time=SimTime(),
            regulation_stage=0,
            infection_above_threshold=False,
        )


    def person_update(self, person: Person) -> None:
        person.step(self._state.sim_time, self._contact_tracer)
        return

def prod_reduced(a: np.array, b: np.array, idx: list) -> tuple:
    """
    return AxB only at desired indices
    """
    return a[idx // b.size], b[idx % b.size]


def comb2_reduced(l: np.array, idx: list) -> tuple:
    """
    return combinations of 2 only at desired indices
    """
    triu = np.triu_indices(l.size, 1)
    return l[triu[0][idx]], l[triu[1][idx]]

@lru_cache(maxsize=None)
def nCk(n: int, k: int) -> int:
    """
    calulate binomial coeffecients
    """
    m = 0
    if k == 0:
        m = 1
    if k == 1:
        m = n
    if k >= 2:
        num, dem, op1, op2 = 1, 1, k, n
        while(op1 >= 1):
            num *= op2
            dem *= op1
            op1 -= 1
            op2 -= 1
        m = num//dem
    return m
