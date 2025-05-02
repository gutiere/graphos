import curses
from curses.textpad import rectangle
import uuid

from graphos.src.utils import get_safe_x, get_safe_y


class Node:
    def __init__(self, x, y, width, height, value=None):
        self.id = str(uuid.uuid4())
        self.value = value
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._update_fields()
        self.grabbed = False
        self.focused = False
        self.selected = False
        # self.color = 1 # Black
        # self.color = 2 # Red
        # self.color = 3 # Green
        # self.color = 4 # Yellow
        # self.color = 5 # Blue
        # self.color = 6 # Pink
        # self.color = 7 # Light Blue
        self.color = 8  # White
        self.grab_color = 4
        self.focus_color = 3
        self.select_color = 7
        self.top_edge = False
        self.bottom_edge = False
        self.left_edge = False
        self.right_edge = False

    def _update_fields(self):
        self.left = self.x
        self.right = self.x + self.width
        self.top = self.y
        self.bottom = self.y + self.height
        self.center = (self.x + self.width // 2, self.y + self.height // 2)
        self.center_x = self.x + self.width // 2
        self.center_y = self.y + self.height // 2
        self.width = max(self.width, len(self.value) + 2)
        self.height = max(self.height, 1)

    def assess_position(self, cursor, offset):
        self.focused = (
            self.left - offset.x <= cursor.x <= self.right - offset.x
            and self.top - offset.y <= cursor.y <= self.bottom - offset.y
        )
        if not self.focused:
            self.grabbed = False

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self._update_fields()

    def move_left(self):
        self.move(-1, 0)

    def move_right(self):
        self.move(1, 0)

    def move_up(self):
        self.move(0, -1)

    def move_down(self):
        self.move(0, 1)

    def reset_edges(self):
        self.top_edge = False
        self.bottom_edge = False
        self.left_edge = False
        self.right_edge = False

    def get_value_coordinate(self, offset):
        padding = (self.width - len(self.value)) // 2

        return (self.x - offset.x + padding + 1, self.center_y - offset.y)

    def render(self, stdscr: curses.window, offset):

        max_y, max_x = stdscr.getmaxyx()

        color = self.color
        if self.grabbed:
            color = self.grab_color
        elif self.selected:
            color = self.select_color
        elif self.focused:
            color = self.focus_color

        normalized_x = self.x - offset.x
        normalized_y = self.y - offset.y
        normalized_y_end = self.y + self.height - offset.y
        normalized_x_end = self.x + self.width - offset.x

        uly = get_safe_y(stdscr, normalized_y)
        ulx = get_safe_x(stdscr, normalized_x)
        lry = get_safe_y(stdscr, normalized_y_end)
        lrx = get_safe_x(stdscr, normalized_x_end)

        if ulx == lrx or uly == lry:
            return

        stdscr.attron(curses.color_pair(color))
        try:
            rectangle(stdscr, uly, ulx, lry, lrx)
        except curses.error:
            # TODO: Debug why this is causing errors. Reproduced when panning a collection of noded down and to the right
            # Handle the case where rectangle goes out of bounds
            pass

        # Draw edge connectors
        if self.bottom_edge and normalized_y_end < max_y and self.center[0] < max_x:
            stdscr.addch(
                get_safe_y(stdscr, normalized_y_end),
                get_safe_x(stdscr, self.center[0] - offset.x),
                curses.ACS_TTEE,
            )
        if self.top_edge and normalized_y > 0 and self.center[0] < max_x:
            stdscr.addch(
                get_safe_y(stdscr, normalized_y),
                get_safe_x(stdscr, self.center[0] - offset.x),
                curses.ACS_BTEE,
            )
        if self.left_edge and normalized_x > 0 and self.center[1] < max_y:
            stdscr.addch(
                get_safe_y(stdscr, self.center[1] - offset.y),
                get_safe_x(stdscr, normalized_x),
                curses.ACS_RTEE,
            )
        if self.right_edge and normalized_x_end < max_x and self.center[1] < max_y:
            stdscr.addch(
                get_safe_y(stdscr, self.center[1] - offset.y),
                get_safe_x(stdscr, normalized_x_end),
                curses.ACS_LTEE,
            )

        stdscr.attroff(curses.color_pair(color))

        # Draw label
        is_trunctated = (
            normalized_y < 0
            or normalized_x < 0
            or normalized_y_end > max_y
            or normalized_x_end > max_x
        )
        if not is_trunctated:
            stdscr.addstr(
                self.get_value_coordinate(offset)[1],
                self.get_value_coordinate(offset)[0],
                self.value,
            )

    def to_JSON(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "value": self.value,
            "grabbed": self.grabbed,
            "focused": self.focused,
            "selected": self.selected,
        }

    @staticmethod
    def from_JSON(data):
        if not isinstance(data, dict):
            raise ValueError("Invalid data format. Expected a dictionary.")
        new_node = Node(
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            value=data["value"],
        )
        new_node.grabbed = data["grabbed"]
        new_node.focused = data["focused"]
        new_node.selected = data["selected"]
        new_node.id = data["id"]
        return new_node
