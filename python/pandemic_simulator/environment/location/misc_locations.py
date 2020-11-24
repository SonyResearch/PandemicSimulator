# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from .base_business import NonEssentialBusinessBaseLocation

__all__ = ['BarberShop']


class BarberShop(NonEssentialBusinessBaseLocation):
    """Implements a barber shop."""

class Restaurant(EssentialBusinessBaseLocation):
    """Implements a restaurant location."""
    pass
