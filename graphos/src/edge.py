"""
Edge module defines objects and functions for
connecting two or more Nodes together.

Intended to be used to convey a relationship between objects
"""

import curses
from dataclasses import dataclass
from typing import Any, Tuple
import uuid

from graphos.src.node import Node
from graphos.src.offset import Offset
from graphos.src.utils import get_safe_x, get_safe_y


@dataclass
class LineSegment:
    """
    Represents a line segment in the graph.

    Attributes:
        type: str type of line segment
        x: int x coordinate
        y: int y coordinate
        length: int length of line
    """

    type: str
    x: int
    y: int
    length: int = 0


class Edge:
    """
    Edge object represents the logical linking between Nodes.

    Attributes:
        source: originating Node for connection
        target: destination Node
        edge_id: unique identifier for Edge, defaults to uuid
    """

    def __init__(self, source: Node, target: Node, edge_id: str = None) -> None:
        self.source = source
        self.target = target

        self.id = edge_id if edge_id else str(uuid.uuid4())

    def __str__(self) -> str:
        """To string definition for Edge"""
        return f"Edge({self.source}, {self.target})"

    def _determine_relative_nodes(self) -> Tuple[Node, Node, Node, Node]:
        """
        Determines the relative positions of nodes based on horizontal
        and vertical locations.

        Returns:
            Tuple of Node objects left, right, top and bottom locations
        """
        node_1, node_2 = self.source, self.target
        left_node = node_1 if node_1.x < node_2.x else node_2
        right_node = node_2 if node_1.x < node_2.x else node_1
        top_node = node_1 if node_1.y < node_2.y else node_2
        bottom_node = node_2 if node_1.y < node_2.y else node_1
        return left_node, right_node, top_node, bottom_node

    def _determine_corner_types(
        self, top_node: Node, bottom_node: Node
    ) -> Tuple[int | None, int | None]:
        """
        Determines the type of corners needed for lines.

        Args:
            top_node: Node that is higher vertically
            bottom_node: Node that is lower in pair

        Returns:
            Tuple of ASCII ints/None
        """
        top_corner = None
        bottom_corner = None
        if top_node.center_x > bottom_node.center_x:
            top_corner = curses.ACS_LRCORNER
            bottom_corner = curses.ACS_ULCORNER
        elif top_node.center_x < bottom_node.center_x:
            top_corner = curses.ACS_LLCORNER
            bottom_corner = curses.ACS_URCORNER
        return top_corner, bottom_corner

    def _has_vertical_bias(self, x_diff: int, y_diff: int) -> bool:
        """
        Determine whether the connection should have a vertical or horizontal bias.

        Args:
            x_diff: Horizontal distance between nodes
            y_diff: Vertical distance between nodes

        Returns:
            bool statement if vertical_bias is present
        """
        return x_diff == 0 or x_diff <= y_diff

    def _create_vertical_connection(
        self,
        left_node: Node,
        right_node: Node,
        top_node: Node,
        bottom_node: Node,
        x_diff: int,
        y_diff: int,
    ) -> list[LineSegment]:
        """
        Create line segments for a vertically biased connection.

        Args:
            left_node: Node on the left
            right_node: Node on the right
            top_node: Node on the top
            bottom_node: Node on the bottom
            x_diff: Horizontal distance between nodes
            y_diff: Vertical distance between nodes

        Returns:
            List of LineSegment objects representing the connection
        """
        lines = []

        # Divide the vertical line into two segments
        y_diff_1 = y_diff // 2
        y_diff_2 = y_diff - y_diff_1

        # Adjust the y-coordinates to account for the node heights
        y_diff_1 -= top_node.height // 2
        y_diff_2 -= bottom_node.height // 2

        top_corner, bottom_corner = self._determine_corner_types(top_node, bottom_node)

        # Calculate horizontal line position
        h_line_x = (
            left_node.center_x
            if left_node.center_x < right_node.center_x
            else right_node.center_x + 1
        )
        h_line_y = bottom_node.center_y - y_diff_2 - bottom_node.height // 2

        # Add horizontal line segment
        lines.append(
            LineSegment(type="horizontal", x=h_line_x, y=h_line_y, length=x_diff)
        )

        # Add corner segments if needed
        if top_corner and bottom_corner:
            lines.append(
                LineSegment(
                    type=top_corner,
                    x=top_node.center_x,
                    y=top_node.center_y + top_node.height // 2 + y_diff_1,
                )
            )
            y_diff_1 -= 1
            y_diff_2 -= 1
            lines.append(
                LineSegment(
                    type=bottom_corner,
                    x=bottom_node.center_x,
                    y=bottom_node.center_y - y_diff_2 - bottom_node.height // 2 - 1,
                )
            )

        # Add vertical line segments
        lines.append(
            LineSegment(
                type="vertical",
                x=top_node.center_x,
                y=top_node.center_y + top_node.height // 2 + 1,
                length=y_diff_1,
            )
        )

        lines.append(
            LineSegment(
                type="vertical",
                x=bottom_node.center_x,
                y=bottom_node.center_y - y_diff_2 - bottom_node.height // 2,
                length=y_diff_2,
            )
        )

        return lines

    def _create_horizontal_connection(
        self,
        left_node: Node,
        right_node: Node,
        top_node: Node,
        bottom_node: Node,
        x_diff: int,
        y_diff: int,
    ) -> list[LineSegment]:
        """
        Create line segments for a horizontally biased connection.

        Args:
            left_node: Node on the left
            right_node: Node on the right
            top_node: Node on the top
            bottom_node: Node on the bottom
            x_diff: Horizontal distance between nodes
            y_diff: Vertical distance between nodes

        Returns:
            List of LineSegment objects representing the connection
        """
        lines = []

        # Divide the horizontal line into two segments
        x_diff_1 = x_diff // 2
        x_diff_2 = x_diff - x_diff_1

        # Adjust the x-coordinates to account for the node widths
        x_diff_1 -= left_node.width // 2
        x_diff_2 -= right_node.width // 2

        # Add first horizontal line segment
        lines.append(
            LineSegment(
                type="horizontal",
                x=left_node.center_x + left_node.width // 2,
                y=left_node.center_y,
                length=x_diff_1,
            )
        )

        # Determine corner types for horizontal connection
        left_corner, right_corner = self._determine_horizontal_corner_types(
            left_node, right_node
        )

        # Calculate vertical line position
        v_line_x = right_node.center_x - x_diff_2 - right_node.width // 2
        v_line_y = (
            bottom_node.center_y
            if bottom_node.center_y < top_node.center_y
            else top_node.center_y + 1
        )

        # Add vertical line segment
        lines.append(
            LineSegment(
                type="vertical",
                x=v_line_x,
                y=v_line_y,
                length=abs(v_line_y + y_diff - v_line_y),
            )
        )

        # Add corner segments if needed
        if left_corner and right_corner:
            x_diff_2 -= 1
            lines.append(
                LineSegment(
                    type=left_corner,
                    x=left_node.center_x + left_node.width // 2 + x_diff_1,
                    y=left_node.center_y,
                )
            )
            lines.append(
                LineSegment(
                    type=right_corner,
                    x=right_node.center_x - x_diff_2 - right_node.width // 2 - 1,
                    y=right_node.center_y,
                )
            )

        # Add second horizontal line segment
        lines.append(
            LineSegment(
                type="horizontal",
                x=right_node.center_x - x_diff_2 - right_node.width // 2,
                y=right_node.center_y,
                length=x_diff_2,
            )
        )

        return lines

    def _determine_horizontal_corner_types(
        self, left_node: Node, right_node: Node
    ) -> Tuple[int | None, int | None]:
        """
        Determines the type of corners needed for horizontal lines.

        Args:
            left_node: Node that is on the left
            right_node: Node that is on the right

        Returns:
            Tuple of ASCII ints for left and right corners
        """
        left_corner = None
        right_corner = None
        if left_node.center_y > right_node.center_y:
            left_corner = curses.ACS_LRCORNER
            right_corner = curses.ACS_ULCORNER
        elif left_node.center_y < right_node.center_y:
            left_corner = curses.ACS_URCORNER
            right_corner = curses.ACS_LLCORNER
        return left_corner, right_corner

    def _convert_line_segments_to_dict(
        self, lines: list[LineSegment]
    ) -> list[dict[str, Any]]:
        """
        Convert LineSegment objects to dictionary format for rendering.

        Args:
            lines: List of LineSegment objects

        Returns:
            List of dictionaries representing line segments
        """
        return [
            {"type": line.type, "x": line.x, "y": line.y, "length": line.length}
            for line in lines
        ]

    def get_line_breakdown(self) -> list[dict[str, Any]]:
        """
        Calculate the line segments needed to connect two nodes.

        This method determines the optimal way to connect nodes with line segments,
        taking into account their relative positions and sizes.

        Returns:
            List of dictionaries representing line segments with their properties
        """
        # Establishes relative node locations (left, right, top, bottom)
        left_node, right_node, top_node, bottom_node = self._determine_relative_nodes()

        # Calculate distances between nodes
        x_diff = abs(right_node.center_x - left_node.center_x)
        y_diff = abs(bottom_node.center_y - top_node.center_y)

        # Determine connection bias (vertical or horizontal)
        has_vertical_bias = self._has_vertical_bias(x_diff, y_diff)

        # Reset edge indicators on nodes
        if has_vertical_bias:
            top_node.reset_edges()
            bottom_node.reset_edges()
            # TODO: Fix the fact that deleting the edge doesn't reset the node edge characters
            # top_node.bottom_edge = True
            # bottom_node.top_edge = True
        else:
            left_node.reset_edges()
            right_node.reset_edges()
            # left_node.right_edge = True
            # right_node.left_edge = True

        # Create appropriate connection based on bias
        if has_vertical_bias:
            line_segments = self._create_vertical_connection(
                left_node, right_node, top_node, bottom_node, x_diff, y_diff
            )
        else:  # horizontal_bias
            line_segments = self._create_horizontal_connection(
                left_node, right_node, top_node, bottom_node, x_diff, y_diff
            )

        # Convert LineSegment objects to dictionaries for rendering
        return self._convert_line_segments_to_dict(line_segments)

    def connect_nodes(self, win: curses.window, offset: Offset) -> None:
        """
        Renders terminal updates based on Node calculations.

        Args:
            win: window to draw in
            offset: Offset for terminal
        """

        lines = self.get_line_breakdown()

        for line in lines:

            normalized_x = line["x"] - offset.x
            normalized_y = line["y"] - offset.y

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
                if (
                    normalized_x < 0
                    or normalized_y < 0
                    or normalized_x >= win.getmaxyx()[1]
                    or normalized_y >= win.getmaxyx()[0]
                ):
                    continue
                win.addch(
                    get_safe_y(win, normalized_y),
                    get_safe_x(win, normalized_x),
                    line["type"],
                )

    def render(self, stdscr: curses.window, offset: Offset) -> None:
        """
        Render the edge on the given window.
        Args:
            stdscr (curses.window): The window to render the edge on.
            offset (Point): The offset to apply to the edge's coordinates.
        """
        self.connect_nodes(stdscr, offset)

    def to_json(self) -> dict[str, Any]:
        """
        Convert the Edge object to a JSON-like dictionary.
        Returns:
            dict: A dictionary representation of the Edge object.
        """

        return {
            "id": self.id,
            "source": self.source.to_json(),
            "target": self.target.to_json(),
        }

    @staticmethod
    def from_json(data: dict[str:any], nodes: list[Node]) -> "Edge":
        """
        Create an Edge object from a JSON-like dictionary.
        Args:
            data (dict): A dictionary containing the edge data.
            nodes (list): A list of Node objects to find the source and target nodes.
        Returns:
            Edge: An Edge object created from the provided data.
        Raises:
            ValueError: An error occurred during rendering the data.
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid data format. Expected a dictionary.")
        if "source" not in data or "target" not in data:
            raise ValueError(
                "Invalid data format. Expected 'source' and 'target' keys."
            )
        if not isinstance(data["source"], dict) or not isinstance(data["target"], dict):
            raise ValueError(
                "Invalid data format. Expected 'source' and 'target' to be dictionaries."
            )
        if "id" not in data["source"] or "id" not in data["target"]:
            raise ValueError(
                "Invalid data format. Expected 'id' key in 'source' and 'target'."
            )
        source_node = next(
            (node for node in nodes if node.id == data["source"]["id"]), None
        )
        if source_node is None:
            raise ValueError(f"Node with id {data['source']['id']} not found.")
        target_node = next(
            (node for node in nodes if node.id == data["target"]["id"]), None
        )
        if target_node is None:
            raise ValueError(f"Node with id {data['target']['id']} not found.")
        new_edge = Edge(
            source=source_node,
            target=target_node,
            edge_id=data["id"],
        )
        return new_edge
