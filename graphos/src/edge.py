from graphos.src.node import Node
import curses

from graphos.src.utils import get_safe_x, get_safe_y


class Edge:
    def __init__(self, source: Node, target: Node):
        self.source = source
        self.target = target

    def get_line_breakdown(self, win: curses.window, node_1: Node, node_2: Node):
        left_node = node_1 if node_1.x < node_2.x else node_2
        right_node = node_2 if node_1.x < node_2.x else node_1
        top_node = node_1 if node_1.y < node_2.y else node_2
        bottom_node = node_2 if node_1.y < node_2.y else node_1

        x_diff = abs(right_node.center_x - left_node.center_x)
        y_diff = abs(bottom_node.center_y - top_node.center_y)

        vertical_bias = False
        horizontal_bias = False

        if x_diff == 0 or x_diff <= y_diff:
            vertical_bias = True
            top_node.reset_edges()
            bottom_node.reset_edges()
            top_node.bottom_edge = True
            bottom_node.top_edge = True
        else:
            horizontal_bias = True
            left_node.reset_edges()
            right_node.reset_edges()
            left_node.right_edge = True
            right_node.left_edge = True

        lines = []
        if vertical_bias:

            # Divide the vertical line into two segments
            y_diff_1 = y_diff // 2
            y_diff_2 = y_diff - y_diff_1

            # Adjust the y-coordinates to account for the node heights
            y_diff_1 -= top_node.height // 2
            y_diff_2 -= bottom_node.height // 2

            top_corner = None
            bottom_corner = None
            if top_node.center_x > bottom_node.center_x:
                top_corner = curses.ACS_LRCORNER
                bottom_corner = curses.ACS_ULCORNER
            elif top_node.center_x < bottom_node.center_x:
                top_corner = curses.ACS_LLCORNER
                bottom_corner = curses.ACS_URCORNER

            h_line_x = (
                left_node.center_x
                if left_node.center_x < right_node.center_x
                else right_node.center_x + 1
            )
            h_line_y = bottom_node.center_y - y_diff_2 - bottom_node.height // 2

            h_line_x_end = get_safe_x(win, h_line_x + x_diff)
            h_line_x = get_safe_x(win, h_line_x)

            lines.append(
                {
                    "type": "horizontal",
                    "x": h_line_x,
                    "y": h_line_y,
                    "length": abs(h_line_x_end - h_line_x),
                }
            )

            if top_corner and bottom_corner:
                lines.append(
                    {
                        "type": top_corner,
                        "x": top_node.center_x,
                        "y": top_node.center_y + top_node.height // 2 + y_diff_1,
                    }
                )
                y_diff_1 -= 1
                y_diff_2 -= 1
                lines.append(
                    {
                        "type": bottom_corner,
                        "x": bottom_node.center_x,
                        "y": bottom_node.center_y
                        - y_diff_2
                        - bottom_node.height // 2
                        - 1,
                    }
                )

            lines.append(
                {
                    "type": "vertical",
                    "x": top_node.center_x,
                    "y": top_node.center_y + top_node.height // 2 + 1,
                    "length": y_diff_1,
                }
            )

            lines.append(
                {
                    "type": "vertical",
                    "x": bottom_node.center_x,
                    "y": bottom_node.center_y - y_diff_2 - bottom_node.height // 2,
                    "length": y_diff_2,
                }
            )
        elif horizontal_bias:

            # Divide the horizontal line into two segments
            x_diff_1 = x_diff // 2
            x_diff_2 = x_diff - x_diff_1

            # Adjust the x-coordinates to account for the node widths
            x_diff_1 -= left_node.width // 2
            x_diff_2 -= right_node.width // 2
            lines.append(
                {
                    "type": "horizontal",
                    "x": left_node.center_x + left_node.width // 2,
                    "y": left_node.center_y,
                    "length": x_diff_1,
                }
            )
            left_corner = None
            right_corner = None
            if left_node.center_y > right_node.center_y:
                left_corner = curses.ACS_LRCORNER
                right_corner = curses.ACS_ULCORNER
            elif left_node.center_y < right_node.center_y:
                left_corner = curses.ACS_URCORNER
                right_corner = curses.ACS_LLCORNER

            v_line_x = right_node.center_x - x_diff_2 - right_node.width // 2
            v_line_y = (
                bottom_node.center_y
                if bottom_node.center_y < top_node.center_y
                else top_node.center_y + 1
            )

            v_line_y_end = get_safe_y(win, v_line_y + y_diff)
            v_line_y = get_safe_y(win, v_line_y)

            lines.append(
                {
                    "type": "vertical",
                    "x": v_line_x,
                    "y": v_line_y,
                    "length": abs(v_line_y_end - v_line_y),
                }
            )
            if left_corner and right_corner:
                x_diff_2 -= 1
                lines.append(
                    {
                        "type": left_corner,
                        "x": left_node.center_x + left_node.width // 2 + x_diff_1,
                        "y": left_node.center_y,
                    }
                )
                lines.append(
                    {
                        "type": right_corner,
                        "x": right_node.center_x - x_diff_2 - right_node.width // 2 - 1,
                        "y": right_node.center_y,
                    }
                )
            lines.append(
                {
                    "type": "horizontal",
                    "x": right_node.center_x - x_diff_2 - right_node.width // 2,
                    "y": right_node.center_y,
                    "length": x_diff_2,
                }
            )

        return lines

    def connect_nodes(self, win: curses.window, node_1: Node, node_2: Node, offset):

        lines = self.get_line_breakdown(win, node_1, node_2)

        for line in lines:

            normalized_x = line["x"] + offset.x
            normalized_y = line["y"] + offset.y

            diff_deduction_x = abs(get_safe_x(win, normalized_x) - normalized_x)
            diff_deduction_y = abs(get_safe_y(win, normalized_y) - normalized_y)


            if line["type"] == "vertical":
                win.vline(
                    get_safe_y(win, normalized_y),
                    get_safe_x(win, normalized_x),
                    curses.ACS_VLINE,
                    line["length"] - diff_deduction_y,
                )
            elif line["type"] == "horizontal":
                win.hline(
                    get_safe_y(win, normalized_y),
                    get_safe_x(win, normalized_x),
                    curses.ACS_HLINE,
                    line["length"] - diff_deduction_x,
                )
            else:
                if normalized_x < 0 or normalized_y < 0 or normalized_x >= win.getmaxyx()[1] or normalized_y >= win.getmaxyx()[0]:
                    continue
                win.addch(
                    get_safe_y(win, normalized_y),
                    get_safe_x(win, normalized_x),
                    line["type"],
                )

    def render(self, stdscr, offset):
        self.connect_nodes(stdscr, self.source, self.target, offset)
