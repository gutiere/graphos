"""Cursor module defines the interface for interacting with the terminal window.

Contains the Cursor class which defines how the coordinates of position in terminal are calculated
"""

from curses import window

from graphos.src.utils import get_safe_x, get_safe_y
from graphos.src.offset import Offset


class Cursor:
    """Defines the cursor object, indicating where the cursor is pointing.

    Attributes:
        x: int x coordinate
        y: int y coordinate
        grab: boolean determining if cursor is set to move objects
        symbol: visual representation of movement cursor
        grab_symbol: visual representation for when grabbing objects
    """

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.grab = False
        self.color = 1
        self.symbol = "🐁"
        self.grab_symbol = "👊"

    def assess_position(self, stdscr: window, offset: Offset) -> None:
        """Checks validity of current cursor position and adjusts if necessary.

        Args:
            stdscr: curses.window object for current screen size
            offset: int
        """

        normalized_x = self.x + offset.x
        normalized_y = self.y + offset.y

        if normalized_x >= stdscr.getmaxyx()[1]:
            self.x = stdscr.getmaxyx()[1] - 2
        if normalized_y >= stdscr.getmaxyx()[0]:
            self.y = stdscr.getmaxyx()[0] - 2

    def toggle_grab(self) -> None:
        """Toggles current grab setting"""
        self.grab = not self.grab

    def render(self, stdscr: window, offset: Offset) -> None:
        """Displays the cursor based on current set locations
        
        Args:
            stdscr: curses.window object for current screen size
            offset: Offset calculator for rendering
        """

        normalized_x = self.x + offset.x
        normalized_y = self.y + offset.y
        normalized_x = get_safe_x(stdscr, normalized_x)
        normalized_y = get_safe_y(stdscr, normalized_y)

        symbol = self.grab_symbol if self.grab else self.symbol
        stdscr.addstr(normalized_y, normalized_x, symbol)
