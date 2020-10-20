# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from .base_business import NonEssentialBusinessBaseLocation
from ..interfaces import PersonID

__all__ = ['Park']


class Park(NonEssentialBusinessBaseLocation):
    """Class that implements a simple park. """

    def assign_person(self, person_id: PersonID) -> None:
        """A person cannot be assigned to a simple park."""
        pass
