"""
Defines the list of constants that are reused across the application.
"""

from dataclasses import dataclass


@dataclass
class Ascii:
    """Ascii maps variable ascii codes to specific fields for use in drawing frames."""

    ROUND_UL_CORNDER = "╭"
    ROUND_UR_CORNER = "╮"
    ROUND_LL_CORNER = "╰"
    ROUND_LR_CORNER = "╯"


MOUSE_OUTPUT = "logging/mouse.log"
LOG_OUTPUT = "logging/application.log"
SAVE_OUTPUT = "user_data/state.json"
