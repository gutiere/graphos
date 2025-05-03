"""
Module functions as the entrypoint into running the graphos utility.
"""

import logging
from pathlib import Path

from curses import wrapper, window

from graphos.src.constants import LOG_OUTPUT, MOUSE_OUTPUT
from graphos.src.view import View
import argparse


def setup_logging() -> None:
    """Instatiates logging interface and expected levels"""
    Path(MOUSE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    Path(LOG_OUTPUT).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=LOG_OUTPUT,
        level=logging.DEBUG,
        format="%(levelname)s - %(message)s",
    )


def setup_args() -> argparse.Namespace:
    """Sets up command line arguments for the utility

    Returns: Namespace object containing parsed arguments
    """
    parser = argparse.ArgumentParser(description="Graphos Utility")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    return parser.parse_args()


def main(window: window) -> None:
    """Operates as the main execution loop for utility

    Args: stdscr: window object for interfacing with terminal
    """
    args = setup_args()
    view = View(window, args)
    view.loop()


wrapper(main)


if __name__ == "__main__":
    wrapper(main)
