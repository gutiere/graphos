"""
Provides the interface for displaying new modal objects on the terminal.

Contains the Modal class, and required functions for building new objects.
"""

# pylint: disable=E1101
import curses
from curses.textpad import Textbox, rectangle

from graphos.src.constants import Ascii
from graphos.src.utils import get_safe_x, get_safe_y


class Modal:
    """
    Defines the popup block for a new modal pane

    Attributes:
        window: curse.window for current terminal
        title: str blurb to display in modal
        content: Provided content for printing in modal
        width: int for total width of modal
        height: int total height for modal
        x: int x coordinate for modal location
        y: int y coordinate for modal location
    """

    def __init__(self, window: curses.window, title: str, content: str = "") -> None:
        self.window = window
        self.title = title
        self.content = content
        self.width = max(len(title) + 4, len(content.split("\n")[0]) + 4)
        self.height = len(content.split("\n")) + 4
        self.x = (curses.COLS - self.width) // 2
        self.y = (curses.LINES - self.height) // 2

    def clear_section(self, uly: int, ulx: int, lry: int, lrx: int) -> None:
        """
        Clears out the section between the coordinate defined through provided boundaries.

        Args:
            uly: int upper left vertical coordinate
            ulx: int upper left horizontal coordinate
            lry: int lower right vertical coordinate
            lrx: int lower right horizontal coordinate
        """
        for y in range(uly, lry):
            for x in range(ulx, lrx):
                self.window.addch(
                    get_safe_y(self.window, y), get_safe_x(self.window, x), " "
                )
        self.window.refresh()

    def render_border(self) -> None:
        """
        Draws the border for the provided modal.
        """
        self.window.attron(curses.color_pair(4))
        self.clear_section(self.y, self.x, self.y + self.height, self.x + self.width)
        rectangle(
            self.window,
            self.y,
            self.x,
            self.y + self.height,
            self.x + self.width,
        )
        self.window.addch(self.y, self.x, Ascii.ROUND_UL_CORNDER)
        self.window.addch(self.y + self.height, self.x, Ascii.ROUND_LL_CORNER)
        self.window.addch(self.y, self.x + self.width, Ascii.ROUND_UR_CORNER)
        self.window.addch(
            self.y + self.height, self.x + self.width, Ascii.ROUND_LR_CORNER
        )
        self.window.refresh()
        self.window.attroff(curses.color_pair(4))

    def render(self) -> None:
        """
        Renders the Modal outline and internal content.
        """
        self.render_border()
        self.window.addstr(self.y + 1, self.x + 2, self.title)
        self.window.refresh()
        editwin = self.window.subwin(1, self.width - 5, self.y + 3, self.x + 3)
        box = Textbox(editwin)
        box.edit()
        self.title = box.gather()
