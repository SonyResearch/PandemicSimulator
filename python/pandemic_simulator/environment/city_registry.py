# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from typing import Dict, List, Optional, cast, Set, Type

from cachetools import cached

from .interfaces import LocationID, Location, PersonID, Person, Registry, RegistrationError, InfectionSummary, \
    IndividualInfectionState, BusinessLocationState, PandemicTestResult
from .location.road import Road

__all__ = ['CityRegistry']


class CityRegistry(Registry):
    """A global registry for all persons and location instances"""

    _location_register: Dict[LocationID, Location]
    _person_register: Dict[PersonID, Person]
    _location_ids: List[LocationID]
    _business_location_ids: List[LocationID]
    _person_ids: List[PersonID]
    _road_id: Optional[LocationID]
    _quarantined: Set[PersonID]

    _location_ids_with_social_events: List[LocationID]

    def __init__(self) -> None:
        self._location_register = {}
        self._person_register = {}
        self._location_ids = []
        self._business_location_ids = []
        self._person_ids = []
        self._quarantined = set()
        self._road_id = None

    def register_location(self, location: Location) -> None:
        """
        Register a location instance

        :param location: Location instance
        :return:
        """

        if isinstance(location, Road):
            if self._road_id is None:
                self._road_id = location.id
            else:
                raise RegistrationError('Only one road location can be registered.')

        if location.id in self._location_register:
            raise RegistrationError(f'Location {location.id.name} is already registered.')
        self._location_register[location.id] = location
        self._location_ids.append(location.id)
        if isinstance(location.state, BusinessLocationState):
            self._business_location_ids.append(location.id)

    def register_person(self, person: Person) -> None:
        """
        Register a person instance

        :param person: Person instance
        """
        if person.id in self._person_register:
            raise RegistrationError(f'Person {person.id.name} is already registered.')

        if person.state.current_location not in self._location_register:
            raise RegistrationError(f'Unable to register the person {person.id.name} because the current'
                                    f'location is not registered yet.')

        for loc_id in person.assigned_locations:
            if loc_id not in self._location_register:
                raise RegistrationError(f'Unable to register the person {person.id.name} because the assigned'
                                        f'location {loc_id.name} is not registered yet.')

        current_location = self._location_register[person.state.current_location]
        assigned_locations = [self._location_register[loc_id] for loc_id in person.assigned_locations]

        if (current_location.id not in person.assigned_locations and
                person.id not in current_location.state.persons_in_location):
            if not current_location.is_entry_allowed(person.id):
                raise RegistrationError('Unable to register the person because the person is not allowed in his/her'
                                        'claimed current location.')

        # everything checks out, register the person
        for loc in assigned_locations:
            loc.assign_person(person.id)
        current_location.add_person_to_location(person.id)
        self._person_register[person.id] = person
        self._person_ids.append(person.id)

    def register_person_entry_in_location(self, person_id: PersonID, location_id: LocationID) -> bool:
        """
        Register a person's entry in the specified location

        :param person_id: PersonID instance
        :param location_id: LocationID instance
        :return: bool to indicate if the registration was successful.
        """
        if self._road_id is None:
            raise RegistrationError('There is no registered road location in the city! Add one.')

        person = self._person_register[person_id]
        current_location = self._location_register[person.state.current_location]
        next_location = self._location_register[location_id]

        if (next_location.id != current_location.id) and not next_location.is_entry_allowed(person_id):
            # if entry to the next location is not allowed
            return False

        # update person and location state
        current_location.remove_person_from_location(person_id)  # exit current
        next_location.add_person_to_location(person_id)  # enter next
        person.state.current_location = next_location.id  # update person state
        return True

    def update_location_specific_information(self) -> None:
        self._location_ids_with_social_events = [loc_id for loc_id, loc in self._location_register.items()
                                                 if loc.state.social_gathering_event]

    @property
    def person_ids(self) -> List[PersonID]:
        return self._person_ids

    @property
    def location_ids(self) -> List[LocationID]:
        return self._location_ids

    @property
    def location_ids_with_social_events(self) -> List[LocationID]:
        return self._location_ids_with_social_events

    @cached(cache={})
    def location_ids_of_type(self, location_type: type) -> List[LocationID]:
        return [loc_id for loc_id, loc in self._location_register.items() if isinstance(loc, location_type)]

    def get_person_home_id(self, person_id: PersonID) -> LocationID:
        return self._person_register[person_id].home

    def get_households(self, person_id: PersonID) -> Set[PersonID]:
        home_id = self._person_register[person_id].home
        home = self._location_register[home_id]
        assignees = home.state.assignees

        return assignees

    def get_person_infection_summary(self, person_id: PersonID) -> Optional[InfectionSummary]:
        if self._person_register[person_id].state.infection_state is not None:
            state = cast(IndividualInfectionState, self._person_register[person_id].state.infection_state)
            return state.summary

        return None

    def get_person_test_result(self, person_id: PersonID) -> PandemicTestResult:
        state = self._person_register[person_id].state
        return state.test_result

    def get_persons_in_location(self, location_id: LocationID) -> Set[PersonID]:
        return self._location_register[location_id].state.persons_in_location

    def location_id_to_type(self, location_id: LocationID) -> Type:
        return type(self._location_register[location_id])

    def reassign_locations(self, person: Person) -> None:
        assigned_locations = [self._location_register[loc_id] for loc_id in person.assigned_locations]
        for loc in assigned_locations:
            loc.assign_person(person.id)

    def quarantine_person(self, person_id: PersonID) -> None:
        self._quarantined.add(person_id)

    def clear_quarantined(self, person_id: PersonID) -> None:
        if person_id in self._quarantined:
            self._quarantined.remove(person_id)

    def get_person_quarantined_state(self, person_id: PersonID) -> bool:
        return person_id in self._quarantined
