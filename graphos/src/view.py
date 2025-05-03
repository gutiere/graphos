import curses
import json
import logging
from pathlib import Path

from graphos.src.constants import LOG_OUTPUT, MOUSE_OUTPUT, SAVE_OUTPUT
from graphos.src.cursor import Cursor
from graphos.src.edge import Edge
from graphos.src.hud import Hud
from graphos.src.menu import Menu
from graphos.src.modal import Modal
from graphos.src.node import Node
from graphos.src.offset import Offset

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename=LOG_OUTPUT,
    level=logging.DEBUG,
    format="%(levelname)s - %(message)s",
)


class View:
    def __init__(self, window: curses.window, args: dict[str:str]) -> None:

        logger.debug("Initializing View")
        logger.debug(f"Start with args: {args}")
        self.args = args

        self.window = window
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

        window_height, window_width = self.window.getmaxyx()

        self.nodes: list[Node] = []
        self.edges: list[Edge] = []

        self.cursor = Cursor(window_width // 2, window_height // 2, self.args)
        self.hud = Hud(window_width, window_height, self.cursor.x, self.cursor.y)
        self.selected_nodes = []
        self.offset = Offset(0, 0)
        self.last_mouse_press = None
        self.menu = None

    def select_node(self, node: Node) -> None:
        if node in self.selected_nodes:
            node.selected = False
            self.selected_nodes.remove(node)
            return

        self.selected_nodes.append(node)
        node.selected = True

        while len(self.selected_nodes) > 2:
            popped_node = self.selected_nodes.pop(0)
            popped_node.selected = False

    def set_last_mouse_press(self, x: int, y: int) -> None:
        """Setter for last position of mouse click"""
        self.last_mouse_press = (x, y)

    def get_last_mouse_press(self) -> tuple[int, int]:
        """Getter function for last mouse click"""
        return self.last_mouse_press

    def setup_keybindings(self):
        self.keybindings = {}
        self.keybindings[curses.KEY_MOUSE] = self.handle_mouse_event
        self.keybindings[curses.KEY_UP] = self.move_cursor_up
        self.keybindings[curses.KEY_DOWN] = self.move_cursor_down
        self.keybindings[curses.KEY_LEFT] = self.move_cursor_left
        self.keybindings[curses.KEY_RIGHT] = self.move_cursor_right
        self.keybindings[ord("a")] = self.pan_left
        self.keybindings[ord("d")] = self.pan_right
        self.keybindings[ord("w")] = self.pan_up
        self.keybindings[ord("s")] = self.pan_down
        self.keybindings[ord("n")] = self.new_node
        self.keybindings[ord("e")] = self.new_edge
        self.keybindings[ord("c")] = self.reset
        self.keybindings[ord("z")] = self.save_state
        self.keybindings[ord("l")] = self.load_state
        self.keybindings[ord("g")] = self.grab
        self.keybindings[ord("q")] = self.quit

    def loop(self):
        curses.beep()

        self.setup_keybindings()

        while True:
            self.render()
            self.handle_input()

    def render(self):

        # # Clear the window
        self.window.clear()

        # Update nodes of cursor state
        for node in self.nodes:
            node.assess_position(self.cursor, self.offset)

        for edge in self.edges:
            edge.render(self.window, self.offset)

        for node in self.nodes:
            if not node.focused:
                node.render(self.window, self.offset)

        for node in self.nodes:
            if node.focused:
                node.render(self.window, self.offset)

        # Draw border around the window
        self.window.border(0)

        # Draw out of view indicator
        number_of_nodes_left_of_pan = 0
        number_of_nodes_right_of_pan = 0
        number_of_nodes_above_pan = 0
        number_of_nodes_below_pan = 0
        for node in self.nodes:
            if node.right <= self.offset.x:
                number_of_nodes_left_of_pan += 1
            if node.left >= self.offset.x + self.window.getmaxyx()[1]:
                number_of_nodes_right_of_pan += 1
            if node.bottom <= self.offset.y:
                number_of_nodes_above_pan += 1
            if node.top >= self.offset.y + self.window.getmaxyx()[0]:
                number_of_nodes_below_pan += 1
        if number_of_nodes_left_of_pan > 0:
            self.window.addstr(self.window.getmaxyx()[0] // 2 - 2, 0, "←")
            self.window.addstr(
                self.window.getmaxyx()[0] // 2, 0, str(number_of_nodes_left_of_pan)
            )
            self.window.addstr(self.window.getmaxyx()[0] // 2 + 2, 0, "←")
        if number_of_nodes_right_of_pan > 0:
            self.window.addstr(
                self.window.getmaxyx()[0] // 2 - 2, self.window.getmaxyx()[1] - 1, "→"
            )
            self.window.addstr(
                self.window.getmaxyx()[0] // 2,
                self.window.getmaxyx()[1] - 1,
                str(number_of_nodes_right_of_pan),
            )
            self.window.addstr(
                self.window.getmaxyx()[0] // 2 + 2, self.window.getmaxyx()[1] - 1, "→"
            )
        if number_of_nodes_above_pan > 0:
            self.window.addstr(0, self.window.getmaxyx()[1] // 2 - 2, "↑")
            self.window.addstr(
                0, self.window.getmaxyx()[1] // 2, str(number_of_nodes_above_pan)
            )
            self.window.addstr(0, self.window.getmaxyx()[1] // 2 + 2, "↑")
        if number_of_nodes_below_pan > 0:
            self.window.addstr(
                self.window.getmaxyx()[0] - 1, self.window.getmaxyx()[1] // 2 - 2, "↓"
            )
            self.window.addstr(
                self.window.getmaxyx()[0] - 1,
                self.window.getmaxyx()[1] // 2,
                str(number_of_nodes_below_pan),
            )
            self.window.addstr(
                self.window.getmaxyx()[0] - 1, self.window.getmaxyx()[1] // 2 + 2, "↓"
            )

        # Draw border around the window
        self.hud.assess_window(
            self.window.getmaxyx()[1],
            self.window.getmaxyx()[0],
            self.cursor.x,
            self.cursor.y,
        )
        self.hud.render(self.window)

        # Draw menu
        # self.menu.x = self.cursor.x
        # self.menu.y = self.cursor.y
        if self.menu is not None:
            self.menu.assess_position(self.cursor.x, self.cursor.y)
            self.menu.render()

        # Draw cursor
        self.cursor.assess_position(self.window, self.offset)
        self.cursor.render(self.window, self.offset)
        self.window.refresh()

    def move_cursor_up(self):
        if self.cursor.y > 1:
            if self.cursor.grab:
                for node in self.nodes:
                    if node.grabbed:
                        node.move_up()
            self.cursor.y -= 1

    def move_cursor_down(self):
        if self.cursor.y < self.window.getmaxyx()[0] - 2:
            if self.cursor.grab:
                for node in self.nodes:
                    if node.grabbed:
                        node.move_down()
            self.cursor.y += 1

    def move_cursor_left(self):
        if self.cursor.x > 1:
            if self.cursor.grab:
                for node in self.nodes:
                    if node.grabbed:
                        node.move_left()
            self.cursor.x -= 1

    def move_cursor_right(self):
        if self.cursor.x < self.window.getmaxyx()[1] - 3:
            if self.cursor.grab:
                for node in self.nodes:
                    if node.grabbed:
                        node.move_right()
            self.cursor.x += 1

    def save_state(self):
        # Save the current state
        state = {
            "nodes": [node.to_JSON() for node in self.nodes],
            "edges": [edge.to_JSON() for edge in self.edges],
        }
        logger.debug(f"Saving state: {state}")
        logger.debug(f"Saving state to {SAVE_OUTPUT}")
        Path(SAVE_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
        with open(SAVE_OUTPUT, "w") as f:
            f.write(json.dumps(state, indent=4))

    def load_state(self):
        # Load the state from the file
        loaded_nodes, loaded_edges = [], []
        try:
            with open(SAVE_OUTPUT, "r") as f:
                state = json.load(f)
                logger.debug(f"Loaded state: {state}")
                loaded_nodes = []
                for node in state["nodes"]:
                    loaded_nodes.append(Node.from_JSON(node))
                loaded_edges = []
                for edge in state["edges"]:
                    loaded_edges.append(Edge.from_JSON(edge, loaded_nodes))
        except FileNotFoundError:
            logger.debug(f"State file {SAVE_OUTPUT} not found.")
        except json.JSONDecodeError:
            logger.debug(f"Error decoding JSON from {SAVE_OUTPUT}.")
        except Exception as e:
            logger.debug(f"Error loading state: {e}")
            logger.debug(f"State file {SAVE_OUTPUT} may be corrupted.")
            return

        if loaded_nodes:
            self.nodes.clear()
            self.edges.clear()
            self.nodes.extend(loaded_nodes)
            self.edges.extend(loaded_edges)

    def pan_left(self):
        self.offset.x -= 1
        # self.cursor.x += 1

    def pan_right(self):
        self.offset.x += 1
        # self.cursor.x -= 1

    def pan_up(self):
        self.offset.y -= 1
        # self.cursor.y += 1

    def pan_down(self):
        self.offset.y += 1
        # self.cursor.y -= 1

    def grab(self):
        # Grab the rectangle
        self.cursor.toggle_grab()
        if self.cursor.grab:
            for node in self.nodes:
                if node.focused:
                    node.grabbed = True
        else:
            for node in self.nodes:
                node.grabbed = False

    def reset(self):
        self.nodes.clear()
        self.edges.clear()
        self.stdscr.clear()

    def new_edge(self):
        if len(self.selected_nodes) == 2:
            for node in self.selected_nodes:
                node.selected = False
            self.edges.append(Edge(self.selected_nodes[0], self.selected_nodes[1]))
            self.selected_nodes.clear()

    def is_node_at_cursor(self):
        for node in self.nodes:
            if node.y == self.cursor.y and node.x == self.cursor.x:
                return True
        return False

    def delete_selected(self):
        for node in self.selected_nodes:
            edges_to_keep = []
            for edge in self.edges:
                if edge.source.id == node.id or edge.target.id == node.id:
                    logger.debug(f"Removing edge {edge} from {node}")
                else:
                    logger.debug(f"Keeping edge {edge} from {node}")
                    edges_to_keep.append(edge)
            self.edges = list(set(edges_to_keep))
            self.nodes.remove(node)
        self.selected_nodes.clear()

    def new_node(self):
        if self.is_node_at_cursor():
            curses.beep()
        else:
            modal = Modal(
                self.window, "Node name (press enter to create, ctrl+h to delete):"
            )
            modal.render()

            new_node = Node(
                x=self.cursor.x + self.offset.x,
                y=self.cursor.y + self.offset.y,
                width=10,
                height=4,
                value=modal.title,
                args=self.args,
            )
            self.nodes.append(new_node)

    def quit(self):
        exit(0)

    def open_create_menu(self):
        options = ["Create node", "Create edge"]
        if len(self.selected_nodes) != 2:
            options.remove("Create edge")

        self.menu = Menu(
            options,
            self.menu.x,
            self.menu.y,
            self.window,
        )

    def open_menu(self, x: int, y: int):
        options = [
            "Create >",
            "Delete selected",
            "Save",
            "Load",
            "Quit",
        ]

        if len(self.selected_nodes) == 0:
            options.remove("Delete selected")

        self.menu = Menu(
            options,
            x,
            y,
            self.window,
        )

    def get_clicked_menu_option(self, x: int, y: int) -> str:
        # Get the objects that were clicked by the cursor

        menu_index = self.menu.get_clicked_option(x, y)
        if menu_index == -1:
            self.menu = None
            logger.debug("No option clicked")
            return None

        menu_option = self.menu.options[menu_index]
        logger.debug(f"Clicked option: {menu_option}")
        return menu_option

    def log_mouse_event(self, event):
        if event[4] != 134217728 and event[4] != 524288:  # Skip noisy movement events
            with open(MOUSE_OUTPUT, "a") as f:
                f.write(f"{event}\n")
            logger.debug(f"Mouse event: {event}")

    def handle_mouse_press(self, x: int, y: int):
        self.set_last_mouse_press(x, y)
        self.cursor.grab = True
        for node in self.nodes:
            node.assess_position(self.cursor, self.offset)
            node.grabbed = node.focused

    def handle_mouse_release(self, x: int, y: int):
        self.cursor.grab = False
        last_mouse_press = self.get_last_mouse_press()
        is_click = last_mouse_press is not None and last_mouse_press == (x, y)
        if is_click:
            logger.debug(f"Clicked at ({x}, {y})")
        else:
            self.menu = None

        click_fulfilled = False
        for node in self.nodes:
            node.assess_position(self.cursor, self.offset)
            if node.focused:
                if is_click:
                    self.select_node(node)
                    click_fulfilled = True
                node.grabbed = False

        # If no node was clicked, show modal for creation
        if not click_fulfilled and is_click:
            if self.menu:
                menu_option = self.get_clicked_menu_option(x, y)
                menu_option_mapping = {}
                menu_option_mapping["Create node"] = self.new_node
                menu_option_mapping["Create edge"] = self.new_edge
                menu_option_mapping["Delete selected"] = self.delete_selected
                menu_option_mapping["Save"] = self.save_state
                menu_option_mapping["Load"] = self.load_state
                menu_option_mapping["Quit"] = self.quit
                menu_option_mapping["Create >"] = self.open_create_menu

                logger.debug(f"Clicked menu option: {menu_option}")
                if menu_option in menu_option_mapping:
                    menu_option_mapping[menu_option]()
                    if menu_option != "Create >":
                        self.menu = None
                    click_fulfilled = True

        if not click_fulfilled and is_click:
            if self.menu is None:
                self.open_menu(x, y)
            else:
                self.menu = None

    def unfocus_all_nodes(self):
        for node in self.nodes:
            node.focused = False
            node.grabbed = False
            node.selected = False

    def handle_mouse_event(self):
        event = curses.getmouse()
        self.log_mouse_event(event)

        _, x, y, _, event_type = event
        if event_type == 2:  # Mouse button pressed
            self.handle_mouse_press(x, y)
        elif event_type == 1:  # Mouse button released
            self.handle_mouse_release(x, y)
        elif event_type == 134217728:  # Mouse moved:

            if self.menu and not self.menu.is_focused(x, y):
                self.menu = None

            if self.cursor.grab:
                node_grabbed = False
                for node in self.nodes:
                    if node.grabbed:
                        node_grabbed = True
                        node.move(x - self.cursor.x, y - self.cursor.y)

                # If no node is grabbed, pan
                if not node_grabbed:
                    self.offset.x -= x - self.cursor.x
                    self.offset.y -= y - self.cursor.y

        if self.args.debug:
            logger.debug(f"Update cursor position to ({x}, {y})")
        self.cursor.x = x
        self.cursor.y = y

    def handle_input(self) -> bool:
        self.keybindings.get(self.window.getch(), lambda: None)()
