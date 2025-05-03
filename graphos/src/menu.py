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

    def __init__(self, options: list[str], x: int, y: int, window: curses.window):
        self.options = options
        self.width = max(len(option) for option in options) + 4
        self.window = window
        self.x = x
        self.y = y
        self.correct_dimentions()
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

    def correct_dimentions(self):
        if self.y <= 0:
            self.y = 1
        if self.x <= 0:
            self.x = 1
        if self.y + len(self.options) + 2 > self.window.getmaxyx()[0]:
            self.y = self.window.getmaxyx()[0] - len(self.options) - 2
        if self.x + self.width > self.window.getmaxyx()[1]:
            self.x = self.window.getmaxyx()[1] - self.width - 2

    def assess_position(self, x: int, y: int):
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

    def get_clicked_option(self, x: int, y: int) -> int:
        """Get the clicked option based on mouse event coordinates."""
        for i, dimensions in enumerate(self.options_dimensions):
            if (
                dimensions["uly"] <= y < dimensions["lry"]
                and dimensions["ulx"] <= x < dimensions["lrx"]
            ):
                return i
        return -1

    def render(self):
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
