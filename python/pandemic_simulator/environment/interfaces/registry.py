# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from abc import ABC, abstractmethod
from typing import List, Optional, Set, Mapping

from .ids import LocationID, PersonID
from .infection_model import InfectionSummary
from .location import Location
from .person import Person
from .pandemic_testing_result import PandemicTestResult

__all__ = ['Registry', 'RegistrationError']


class RegistrationError(Exception):
    """An error raised by the CityRegistry"""


class Registry(ABC):
    """A global registry for all persons and location instances"""

    @abstractmethod
    def register_location(self, location: Location) -> None:
        """
        Register a location instance

        :param location: Location instance
        :return:
        """

    @abstractmethod
    def register_person(self, person: Person) -> None:
        """
        Register a person instance

        :param person: Person instance
        """

    @abstractmethod
    def register_person_entry_in_location(self, person_id: PersonID, location_id: LocationID) -> bool:
        """
        Register a person's entry in the specified location

        :param person_id: PersonID instance
        :param location_id: LocationID instance
        :return: bool to indicate if the registration was successful.
        """

    @abstractmethod
    def update_location_specific_information(self) -> None:
        """update any location specific information that is accessed by person."""

    @property
    @abstractmethod
    def person_ids(self) -> List[PersonID]:
        """Return a list of registered person ids"""
        pass

    @property
    @abstractmethod
    def location_ids(self) -> List[LocationID]:
        """Return a list of registered location ids"""
        pass

    @property
    @abstractmethod
    def location_ids_with_social_events(self) -> List[LocationID]:
        """Return a list of location ids where there are active social events."""

    @property
    @abstractmethod
    def location_occupancy_summary(self) -> Mapping[str, int]:
        """Return a mapping between a location type name and the number of persons in that location type.
           E.g.: {'Hospital': 10}
        """

    @abstractmethod
    def location_ids_of_type(self, location_type: type) -> List[LocationID]:
        """Return a list of location ids for the given type of location."""

    @abstractmethod
    def get_person_home_id(self, person_id: PersonID) -> LocationID:
        """Return person's home id"""

    @abstractmethod
    def get_households(self, person_id: PersonID) -> Set[PersonID]:
        """Return person's households"""

    @abstractmethod
    def get_person_infection_summary(self, person_id: PersonID) -> Optional[InfectionSummary]:
        """Return person's infection summary"""

    @abstractmethod
    def get_person_test_result(self, person_id: PersonID) -> PandemicTestResult:
        """Return person's test result"""

    @abstractmethod
    def get_persons_in_location(self, location_id: LocationID) -> Set[PersonID]:
        """Return a list of persons in the given location"""

    @abstractmethod
    def location_id_to_type(self, location_id: LocationID) -> type:
        """Return the type of location with the given ID."""

    @abstractmethod
    def reassign_locations(self, person: Person) -> None:
        """Re-assign locations for the given person."""

    @abstractmethod
    def quarantine_person(self, person_id: PersonID) -> None:
        """Mark person to be quarantined."""

    @abstractmethod
    def clear_quarantined(self, person_id: PersonID) -> None:
        """Clear person's quarantined information."""

    @abstractmethod
    def get_person_quarantined_state(self, person_id: PersonID) -> bool:
        """Return person's quarantined state."""
