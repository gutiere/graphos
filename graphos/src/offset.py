"""
Offset module Establishes the offset for the given terminal being used
"""

from dataclasses import dataclass


@dataclass
class Offset:
    """
    Offset object contains the x and y coordinate offset definitions

    Attributes:
        x: int x coordinate
        y: int y coordinate
    """

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y
