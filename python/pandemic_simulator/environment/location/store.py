# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.

__all__ = ['GroceryStore', 'RetailStore']

from .base_business import EssentialBusinessBaseLocation, NonEssentialBusinessBaseLocation


class GroceryStore(EssentialBusinessBaseLocation):
    """Implements a grocery store location."""
    pass


class RetailStore(NonEssentialBusinessBaseLocation):
    """Implements a retail store location."""
    pass
