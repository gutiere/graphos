from graphos.src.utils import get_safe_x, get_safe_y


class Cursor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.grab = False
        self.color = 1
        self.symbol = "🐁"
        self.grab_symbol = "👊"

    def assess_position(self, stdscr, cursor, offset):
        self.x = cursor.x
        self.y = cursor.y

        normalized_x = self.x + offset.x
        normalized_y = self.y + offset.y

        if normalized_x >= stdscr.getmaxyx()[1]:
            self.x = stdscr.getmaxyx()[1] - 2
        if normalized_y >= stdscr.getmaxyx()[0]:
            self.y = stdscr.getmaxyx()[0] - 2

    def toggle_grab(self):
        self.grab = not self.grab

    def render(self, stdscr, offset):

        normalized_x = self.x + offset.x
        normalized_y = self.y + offset.y
        normalized_x = get_safe_x(stdscr, normalized_x)
        normalized_y = get_safe_y(stdscr, normalized_y)

        symbol = self.grab_symbol if self.grab else self.symbol
        stdscr.addstr(normalized_y, normalized_x, symbol)
