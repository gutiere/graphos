from curses import wrapper
import curses

import logging
from pathlib import Path
from graphos.src.constants import LOG_OUTPUT, MOUSE_OUTPUT
from graphos.src.view import View


def setup_logging():
    Path(MOUSE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    Path(LOG_OUTPUT).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=LOG_OUTPUT,
        level=logging.DEBUG,
        format="%(levelname)s - %(message)s",
    )


def main(stdscr):
    view = View(stdscr)
    view.loop()

curses.wrapper(main)


if __name__ == "__main__":
    wrapper(main)
