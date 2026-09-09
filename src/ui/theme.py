"""UI Theme and styling constants for GH-BOT-REPOS dark mode."""

from __future__ import annotations


class Theme:
    """Color palette and fonts for pure solid black & electric blue theme."""

    # Pure Solid Black Everywhere (Opaque #000000)
    BG_MAIN = "#000000"       # Pure solid black main background
    BG_SIDEBAR = "#000000"    # Pure solid black sidebar
    BG_CARD = "#000000"       # Pure solid black cards
    BG_CARD_HOVER = "#0A0A0A" # Subtle black hover
    BG_INPUT = "#000000"      # Pure solid black input surface
    BG_GLASS_PILL = "#000000"

    # Black Borders
    BORDER = "#141414"        # Dark black border
    BORDER_GLOW = "#1A1A1A"
    BORDER_CYAN = "#0066FF"

    # Buttons (Vibrant Electric Blue)
    PRIMARY = "#0066FF"       # Vibrant strong blue
    PRIMARY_HOVER = "#1A75FF" # Hover blue
    BTN_SECONDARY = "#0052CC" # Secondary button blue
    BTN_SECONDARY_HOVER = "#0066FF" # Secondary hover blue
    SUCCESS = "#10B981"       # Emerald green for status
    WARNING = "#F59E0B"       # Amber warning
    ERROR = "#EF4444"         # Coral red error

    # Typography (Pure White)
    TEXT_PRIMARY = "#FFFFFF"   # Pure white
    TEXT_SECONDARY = "#FFFFFF" # Pure white for secondary text
    TEXT_MUTED = "#A0A0A0"     # Light clear white-gray text

    # Fonts (Safe standard Windows fonts)
    FONT_FAMILY = "Segoe UI"
    FONT_TITLE = ("Segoe UI", 18, "bold")
    FONT_SUBTITLE = ("Segoe UI", 14, "bold")
    FONT_BODY = ("Segoe UI", 12)
    FONT_BODY_BOLD = ("Segoe UI", 12, "bold")
    FONT_SMALL = ("Segoe UI", 10)
    FONT_MONO = ("Consolas", 10)

