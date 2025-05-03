"""
Defines the full outline for the terminal, as a drawing pane.

This includes the frame, as well as HUD information and coordinate locations.
"""

import curses
from curses.textpad import rectangle
import logging
from graphos.src.constants import LOG_OUTPUT
from graphos.src.utils import clear_section

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename=LOG_OUTPUT,
    level=logging.DEBUG,
    format="%(levelname)s - %(message)s",
)


class Menu:
    """
    Menu serves as the main pane for drawing in the target terminal.
    This includes helpful HUD information.

    Attributes:
        options: list[str] set of available actions
        window: curses.window object for drawing
        x: int current x coordinate
        y: int current y coordinate
        dimensions: dict boundary coordinates for menu
        option_dimensions: list dict object containing coordinate sizes of each option
        selected_option: indicates current user selected option based on cursor location
    """

    def __init__(self, options: list[str], x: int, y: int, window: curses.window):
        self.options = options
        self.width = max(len(option) for option in options) + 4
        self.window = window
        self.x = x
        self.y = y
        self.correct_dimensions()
        self.dimensions = {
            "uly": self.y,
            "ulx": self.x,
            "lry": self.y + len(self.options) + 1,
            "lrx": self.x + self.width,
        }
        self.options_dimensions = []
        for i in range(len(options)):
            self.options_dimensions.append(
                {
                    "uly": self.y + i + 1,
                    "ulx": self.x + 2,
                    "lry": self.y + i + 2,
                    "lrx": self.x + self.width - 2,
                }
            )
        self.selected_option = -1

    def correct_dimensions(self) -> None:
        """
        Sanitizes coordinates to be within window.
        Sets x and y attributes.
        """
        if self.y <= 0:
            self.y = 1
        if self.x <= 0:
            self.x = 1
        if self.y + len(self.options) + 2 > self.window.getmaxyx()[0]:
            self.y = self.window.getmaxyx()[0] - len(self.options) - 2
        if self.x + self.width > self.window.getmaxyx()[1]:
            self.x = self.window.getmaxyx()[1] - self.width - 2

    def assess_position(self, x: int, y: int) -> None:
        """
        Checks provided location against known option boundaries.
        Sets option if it is within stored boundaries.

        Args:
            x: int x coordinate
            y: int y coordinate
        """
        # Keep track of which option is highlighted
        for i, dimensions in enumerate(self.options_dimensions):
            if (
                dimensions["uly"] <= y < dimensions["lry"]
                and dimensions["ulx"] <= x < dimensions["lrx"]
            ):
                self.selected_option = i
                break
        else:
            self.selected_option = -1

    def is_focused(self, x: int, y: int) -> bool:
        """
        Check if the mouse event is within the menu dimensions.
        
        Args:
            x: int x coordinate
            y: int y coordinate
        """
        return (
            self.dimensions["uly"] <= y < self.dimensions["lry"]
            and self.dimensions["ulx"] <= x < self.dimensions["lrx"]
        )

    def get_clicked_option(self, x: int, y: int) -> int:
        """
        Get the clicked option based on mouse event coordinates.
        
        Args:
            x: int x coordinate
            y: int y coordinate
        """
        for i, dimensions in enumerate(self.options_dimensions):
            if (
                dimensions["uly"] <= y < dimensions["lry"]
                and dimensions["ulx"] <= x < dimensions["lrx"]
            ):
                return i
        return -1

    def render(self) -> None:
        """
        Draws the menu content in the terminal.
        """
        clear_section(self.window, **self.dimensions)
        try:
            rectangle(self.window, **self.dimensions)
        except curses.error:
            logger.error("Error drawing rectangle in menu.")

        default_color = curses.color_pair(4)
        selected_color = curses.color_pair(5)
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                self.window.attron(selected_color)
            else:
                self.window.attron(default_color)
            self.window.addstr(
                self.y + i + 1,
                self.x + 2,
                option,
            )
            self.window.refresh()
            if i == self.selected_option:
                self.window.attroff(selected_color)
            else:
                self.window.attroff(default_color)
        self.window.refresh()
