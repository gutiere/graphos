"""
Utility module for storing shared functions across all package modules.
"""

import curses


def get_safe_x(
    stdscr: curses.window,
    x: int,
) -> int:
    """
    Get a safe x coordinate for rendering within the window bounds.

    Args:
        stdscr: curses.window for interacting with
        y: int current y coordinate

    Returns:
        int coordinate for x
    """
    max_x = stdscr.getmaxyx()[1]
    if x < 0:
        return 0
    if x >= max_x:
        return max_x - 1
    return x


def get_safe_y(
    stdscr: curses.window,
    y: int,
) -> int:
    """
    Get a safe y coordinate for rendering within the window bounds.

    Args:
        stdscr: curses.window for interacting with
        y: int current y coordinate

    Returns:
        int coordinate for x
    """
    max_y = stdscr.getmaxyx()[0]
    if y < 0:
        return 0
    if y >= max_y:
        return max_y - 1
    return y


def clear_section(window, uly: int, ulx: int, lry: int, lrx: int) -> None:
    """
    Clears out the section between the boundary provided.

    Args:
        uly: int upper left vertical coordinate
        ulx: int upper left horizontal coordinate
        lry: int lower right vertical coordinate
        lrx: int lower right horizontal coordinate
    """
    for y in range(uly, lry):
        for x in range(ulx, lrx):
            window.addch(get_safe_y(window, y), get_safe_x(window, x), " ")
    window.refresh()
