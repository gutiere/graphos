import curses


def get_safe_x(
    stdscr: curses.window,
    x: int,
) -> int:
    """
    Get a safe x coordinate for rendering within the window bounds.
    """
    max_x = stdscr.getmaxyx()[1]
    if x < 0:
        return 0
    elif x >= max_x:
        return max_x - 1
    return x


def get_safe_y(
    stdscr: curses.window,
    y: int,
) -> int:
    """
    Get a safe y coordinate for rendering within the window bounds.
    """
    max_y = stdscr.getmaxyx()[0]
    if y < 0:
        return 0
    elif y >= max_y:
        return max_y - 1
    return y


def clear_section(window, uly, ulx, lry, lrx):
    for y in range(uly, lry):
        for x in range(ulx, lrx):
            window.addch(get_safe_y(window, y), get_safe_x(window, x), " ")
    window.refresh()
