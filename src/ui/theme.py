"""UI Theme and styling constants for GH-BOT-REPOS dark mode."""

from __future__ import annotations


class Theme:
    """Color palette and fonts for modern Windows Dark Mode."""

    # Colors (Deep Black + Strong Midnight Blue)
    BG_MAIN = "#08090C"
    BG_SIDEBAR = "#040507"
    BG_CARD = "#0F131C"
    BG_CARD_HOVER = "#161C2A"
    BG_INPUT = "#0A0D14"
    BORDER = "#1E2738"

    # Accents (Strong Electric Blue & Indicators)
    PRIMARY = "#0066FF"
    PRIMARY_HOVER = "#0052CC"
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
