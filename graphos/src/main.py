from curses import wrapper
import curses

import curses
from curses.textpad import Textbox, rectangle

import curses
import json
import logging
from pathlib import Path

from graphos.src.edge import Edge
from graphos.src.menu import Menu
from graphos.src.node import Node
from graphos.src.cursor import Cursor
from graphos.src.offset import Offset

MOUSE_OUTPUT = "logging/mouse.txt"
Path(MOUSE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)

LOG_OUTPUT = "logging/log.txt"
Path(LOG_OUTPUT).parent.mkdir(parents=True, exist_ok=True)


logging.basicConfig(
    filename=LOG_OUTPUT,
    level=logging.DEBUG,
    format="%(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

logger.info("Starting the application")


def handle_input(
    stdscr,
    key,
    cursor,
    nodes: list[Node],
    edges,
    window_width,
    window_height,
    offset,
    selected_nodes,
    select_node,
    set_last_mouse_press,
    get_last_mouse_press,
) -> bool:
    if key != curses.KEY_MOUSE:
        logger.debug(f"Key: {key}")
    if key == curses.KEY_UP and cursor.y > 1:
        if cursor.grab:
            for node in nodes:
                if node.grabbed:
                    node.move_up()
        cursor.y -= 1
    elif key == curses.KEY_DOWN and cursor.y < window_height - 2:
        if cursor.grab:
            for node in nodes:
                if node.grabbed:
                    node.move_down()
        cursor.y += 1
    elif key == curses.KEY_LEFT and cursor.x > 1:
        if cursor.grab:
            for node in nodes:
                if node.grabbed:
                    node.move_left()
        cursor.x -= 1
    elif key == curses.KEY_RIGHT and cursor.x < window_width - 3:
        if cursor.grab:
            for node in nodes:
                if node.grabbed:
                    node.move_right()
        cursor.x += 1

    elif key == ord("z"):
        # Save the current state
        state = {
            "nodes": nodes,
            "edges": edges,
        }
        with open("resources/save.json", "w") as f:
            f.write(json.dumps(state, indent=4))

    elif key == curses.KEY_MOUSE:
        event = curses.getmouse()
        if event[4] != 134217728:
            logger.debug(f"Mouse event: {event}")
            with open(MOUSE_OUTPUT, "a") as f:
                f.write(f"{event}\n")
        
        y = event[2]
        x = event[1]
        event_type = event[4]
        if event_type == 2:  # Mouse button pressed
            set_last_mouse_press(x, y)
            cursor.grab = True
            for node in nodes:
                node.assess_position(cursor)
                if node.focused:
                    node.grabbed = True
        elif event_type == 1:  # Mouse button released
            last_mouse_press = get_last_mouse_press()
            cursor.grab = False
            for node in nodes:
                node.assess_position(cursor)
                if node.focused:
                    logger.debug(f"x: {x}, y: {y}")
                    logger.debug(f"cursor.x: {cursor.x}, cursor.y: {cursor.y}")
                    logger.debug(f"last_mouse_press: {last_mouse_press}")
                    if last_mouse_press is not None and last_mouse_press == (x, y):
                        logger.debug(f"Clicked on node: {node.value}")
                        select_node(node)
                    node.grabbed = False
        if cursor.grab:
            for node in nodes:
                if node.grabbed:
                    node.move(x - cursor.x, y - cursor.y)

        cursor.x = x
        cursor.y = y

    elif key == ord("a"):
        offset.x -= 1
        cursor.x += 1  # Prevents cursor from going out of bounds
    elif key == ord("d"):
        offset.x += 1
        cursor.x -= 1  # Prevents cursor from going out of bounds
    elif key == ord("w"):
        offset.y -= 1
        cursor.y += 1  # Prevents cursor from going out of bounds
    elif key == ord("s"):
        offset.y += 1
        cursor.y -= 1  # Prevents cursor from going out of bounds
    elif key == ord("g"):
        # Grab the rectangle
        cursor.toggle_grab()
        if cursor.grab:
            for node in nodes:
                if node.focused:
                    node.grabbed = True
        else:
            for node in nodes:
                node.grabbed = False
    elif key == ord("c"):
        # Clear the screen
        nodes.clear()
        edges.clear()
        stdscr.clear()
    elif key == ord("e"):
        if len(selected_nodes) == 2:
            for node in selected_nodes:
                node.selected = False
            edges.append(Edge(selected_nodes[0], selected_nodes[1]))
            selected_nodes.clear()
    elif key == ord("n"):
        skip = False
        for node in nodes:
            if node.y == cursor.y and node.x == cursor.x:
                skip = True
                break

        if skip:
            curses.beep()
        else:
            # Create a new window for the textbox
            editwin = curses.newwin(1, 30, cursor.y, cursor.x)
            rectangle(
                stdscr, cursor.y - 1, cursor.x - 2, cursor.y + 2, cursor.x + 45 + 1
            )
            stdscr.addstr(cursor.y - 1, cursor.x - 2, "Node name (ctrl+h to delete, enter to create): ")
            stdscr.refresh()

            # Create a Textbox object
            box = Textbox(editwin)

            # Let the user edit until Ctrl-G is struck.
            box.edit()

            # Get resulting contents
            text = box.gather()

            new_node = Node(x=cursor.x, y=cursor.y, width=10, height=4, value=text)
            nodes.append(new_node)
            curses.beep()
    elif key == ord("q"):
        exit(0)


def main(stdscr):

    # Enable mouse events
    curses.mouseinterval(0)  # Set mouse interval to 0 for immediate response
    curses.mousemask(curses.REPORT_MOUSE_POSITION | curses.ALL_MOUSE_EVENTS)
    print("\033[?1003h")

    # Initialize curses color
    curses.start_color()
    curses.use_default_colors()
    for i in range(curses.COLORS - 1):
        curses.init_pair(i + 1, i, -1)
    # Hide the cursor
    curses.curs_set(0)
    stdscr.clear()

    window_height, window_width = stdscr.getmaxyx()

    nodes: list[Node] = []
    edges: list[Edge] = []

    cursor = Cursor(window_width // 2, window_height // 2)
    menu = Menu(window_width, window_height, nodes, cursor.x, cursor.y)

    selected_nodes = []

    offset = Offset(0, 0)

    def select_node(node: Node):
        if node in selected_nodes:
            node.selected = False
            selected_nodes.remove(node)
            return
        
        selected_nodes.append(node)
        node.selected = True

        while len(selected_nodes) > 2:
            popped_node = selected_nodes.pop(0)
            popped_node.selected = False

    last_mouse_press = None
    def set_last_mouse_press(x, y):
        nonlocal last_mouse_press
        last_mouse_press = (x, y)

    def get_last_mouse_press():
        nonlocal last_mouse_press
        return last_mouse_press

    while True:

        window_height, window_width = stdscr.getmaxyx()

        # Clear the screen
        stdscr.clear()

        # Update nodes of cursor state
        for node in nodes:
            node.assess_position(cursor)

        for edge in edges:
            edge.render(stdscr, offset)

        for node in nodes:
            if not node.focused:
                node.render(stdscr, offset)

        for node in nodes:
            if node.focused:
                node.render(stdscr, offset)

        # Draw border around the window
        stdscr.border(0)

        # Draw border around the window
        menu.assess_window(window_width, window_height, nodes, cursor.x, cursor.y)
        menu.render(stdscr)

        # Draw cursor
        cursor.assess_position(stdscr, cursor, offset)
        cursor.render(stdscr, offset)

        # Get user input
        handle_input(
            stdscr,
            stdscr.getch(),
            cursor,
            nodes,
            edges,
            window_width,
            window_height,
            offset,
            selected_nodes,
            select_node,
            set_last_mouse_press,
            get_last_mouse_press,
        )

        # Refresh the screen
        stdscr.refresh()


curses.wrapper(main)


if __name__ == "__main__":
    wrapper(main)
