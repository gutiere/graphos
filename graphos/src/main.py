"""
Module functions as the entrypoint into running the graphos utility.
"""

from curses import wrapper
import curses

import logging
from pathlib import Path
from graphos.src.constants import LOG_OUTPUT, MOUSE_OUTPUT
from graphos.src.view import View


def setup_logging():
    """Instatiates logging interface and expected levels"""
    Path(MOUSE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    Path(LOG_OUTPUT).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=LOG_OUTPUT,
        level=logging.DEBUG,
        format="%(levelname)s - %(message)s",
    )


def main(stdscr: curses.window) -> None:
    """Operates as the main execution loop for utility

    Args: stdscr: window object for interfacing with terminal
    """
    view = View(stdscr)
    view.loop()


curses.wrapper(main)


if __name__ == "__main__":
    wrapper(main)
