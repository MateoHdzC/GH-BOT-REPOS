"""UI Theme and styling constants for GH-BOT-REPOS dark mode."""

from __future__ import annotations


class Theme:
    """Color palette and fonts for modern Windows Dark Mode."""

    # Colors
    BG_MAIN = "#141416"
    BG_SIDEBAR = "#1C1C1F"
    BG_CARD = "#232328"
    BG_CARD_HOVER = "#2C2C32"
    BG_INPUT = "#1B1B1E"
    BORDER = "#323238"

    # Accents
    PRIMARY = "#0A84FF"
    PRIMARY_HOVER = "#0071E3"
    SUCCESS = "#30D158"
    WARNING = "#FF9F0A"
    ERROR = "#FF453A"

    # Typography
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#9E9EA7"
    TEXT_MUTED = "#6C6C75"

    # Fonts (Safe standard Windows fonts)
    FONT_FAMILY = "Segoe UI"
    FONT_TITLE = ("Segoe UI", 18, "bold")
    FONT_SUBTITLE = ("Segoe UI", 14, "bold")
    FONT_BODY = ("Segoe UI", 12)
    FONT_BODY_BOLD = ("Segoe UI", 12, "bold")
    FONT_SMALL = ("Segoe UI", 10)
    FONT_MONO = ("Consolas", 10)
