import curses
from graphos.src.cursor import Cursor
from graphos.src.offset import Offset


class Hud:
    def __init__(self, window: curses.window, cursor: Cursor, offset: Offset):
        window_height, window_width = window.getmaxyx()
        self.assess_window(window_width, window_height, cursor, offset)

    def assess_window(
        self, window_width, window_height, cursor: Cursor, offset: Offset
    ):
        self.window_width = window_width
        self.window_height = window_height
        self.cursor = cursor
        self.offset = offset

    def render(self, window: curses.window):

        pan_string = f"pan: ([{0 + self.offset.x},{self.window_width + self.offset.x }], [{0 + self.offset.y}, {self.window_height + self.offset.y}])"
        cursor_string = f"cursor: ({self.cursor.x}/{self.window_width}, {self.cursor.y}/{self.window_height})"
        if self.cursor.grab:
            hud_string = f" {pan_string} "
        else:
            hud_string = f" {cursor_string} "
        hud_string = f" {pan_string} {cursor_string} "
        # hud_string = f" x: [{0 + self.offset.x} : {self.cursor.x} : {self.window_width + self.offset.x }], y: [{0 + self.offset.y} : {self.cursor.y} : {self.window_height + self.offset.y }] "

        window.addstr(
            self.window_height - 1,
            self.window_width - len(hud_string) - 1,
            hud_string,
        )
