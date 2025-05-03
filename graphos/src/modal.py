"""
Provides the interface for displaying new modal objects on the terminal.

Contains the Modal class, and required functions for building new objects.
"""

# pylint: disable=E1101
import curses
from curses.textpad import Textbox, rectangle

from graphos.src.constants import Ascii
from graphos.src.utils import clear_section


class Modal:
    """
    Defines the popup pane for a new modal.

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

    def render_border(self) -> None:
        """
        Draws the border for the provided modal.
        """
        self.window.attron(curses.color_pair(4))
        clear_section(
            self.window, self.y, self.x, self.y + self.height, self.x + self.width
        )
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
        Renders the Modal.
        """
        self.render_border()
        self.window.addstr(self.y + 1, self.x + 2, self.title)
        self.window.refresh()
        editwin = self.window.subwin(1, self.width - 5, self.y + 3, self.x + 3)
        box = Textbox(editwin)
        box.edit()
        self.title = box.gather()
