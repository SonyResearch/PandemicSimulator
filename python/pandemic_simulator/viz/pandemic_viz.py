# Confidential, Copyright 2020, Sony Corporation of America, All rights reserved.
from abc import ABC, abstractmethod
from typing import Any

__all__ = ['PandemicViz']


class PandemicViz(ABC):
    """An interface for Pandemic19 visualization"""

    @abstractmethod
    def record(self, data: Any, **kwargs: Any) -> None:
        """
        Record data to internals for plotting.

        :param data:
        :param kwargs: other optional keyword args
        """

    def plot(self) -> None:
        """Make plots"""
