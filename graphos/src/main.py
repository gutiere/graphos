"""
Module functions as the entrypoint into running the graphos utility.
"""

import logging
from pathlib import Path

from curses import wrapper, window

from graphos.src.constants import LOG_OUTPUT, MOUSE_OUTPUT
from graphos.src.view import View


def setup_logging() -> None:
    """Instatiates logging interface and expected levels"""
    Path(MOUSE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    Path(LOG_OUTPUT).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=LOG_OUTPUT,
        level=logging.DEBUG,
        format="%(levelname)s - %(message)s",
    )


def main(stdscr: window) -> None:
    """Operates as the main execution loop for utility

    Args: stdscr: window object for interfacing with terminal
    """
    view = View(stdscr)
    view.loop()


wrapper(main)


if __name__ == "__main__":
    wrapper(main)
