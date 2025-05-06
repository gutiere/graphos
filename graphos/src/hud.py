"""
HUD module defines helpful information displayed
around current grid coordinates.
"""

import curses

from graphos.src.cursor import Cursor
from graphos.src.offset import Offset


class Hud:
    """
    HUD definition for printing helpful coordinate infomation.

    Attributes:
        window_height: Defined height of terminal
        window_width: defined width of terminal
        cursor: cursor object for HUD
        offset: tracker for coordinate shift
    """

    def __init__(self, window: curses.window, cursor: Cursor, offset: Offset) -> None:
        window_height, window_width = window.getmaxyx()
        self.window_width = window_width
        self.window_height = window_height
        self.cursor = cursor
        self.offset = offset

    def build_hud_string(self) -> str:
        """
        Builds HUD information display string.

        Returns:
            string for printing in terminal
        """
        pan_x = f"[{0 + self.offset.x},{self.window_width + self.offset.x }]"
        pan_y = f"[{0 + self.offset.y}, {self.window_height + self.offset.y}]"
        pan_string = f"pan: ({pan_x}, {pan_y})"

        cur_x = f"{self.cursor.x}/{self.window_width}"
        cur_y = f"{self.cursor.y}/{self.window_height}"
        cursor_string = f"cursor: ({cur_x}, {cur_y})"
        if self.cursor.grab:
            hud_string = f" {pan_string} "
        else:
            hud_string = f" {cursor_string} "
        hud_string = f" {pan_string} {cursor_string}"
        return hud_string

    def render(self, window: curses.window) -> None:
        """
        Renders the HUD information display
        """
        hud_string = self.build_hud_string()
        window.addstr(
            self.window_height - 1,
            self.window_width - len(hud_string) - 1,
            hud_string,
        )
