class Menu:
    def __init__(self, window_width, window_height, x, y):
        self.assess_window(window_width, window_height, x, y)

    def assess_window(self, window_width, window_height, x, y):
        self.window_width = window_width
        self.window_height = window_height
        self.x = x
        self.y = y

    def render(self, stdscr):
        hud_string = f" ({self.x}/{self.window_width}, {self.y}/{self.window_height}) "
        stdscr.addstr(
            self.window_height - 1,
            self.window_width - len(hud_string) - 1,
            hud_string,
        )
