"""
Offset module is used to help calculate the offset of rendered items when panning the view.
"""

from dataclasses import dataclass


@dataclass
class Offset:
    """
    Offset object contains the x and y coordinate offset definitions to track panning movements.
    
    Attributes:
        x: int x coordinate
        y: int y coordinate
    """

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y
