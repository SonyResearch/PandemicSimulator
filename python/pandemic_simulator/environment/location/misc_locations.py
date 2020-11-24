# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

from .base_business import NonEssentialBusinessBaseLocation

__all__ = ['BarberShop', 'Restaurant']


class BarberShop(NonEssentialBusinessBaseLocation):
    """Implements a barber shop."""


class Restaurant(NonEssentialBusinessBaseLocation):
    """Implements a restaurant location."""
    pass
