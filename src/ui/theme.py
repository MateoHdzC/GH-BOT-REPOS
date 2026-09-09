"""UI Theme and styling constants for GH-BOT-REPOS dark mode."""

from __future__ import annotations


class Theme:
    """Color palette and fonts for pure black & electric blue theme."""

    # Pure Black Surfaces
    BG_MAIN = "#000000"       # Pure black main background
    BG_SIDEBAR = "#000000"    # Pure black sidebar background
    BG_CARD = "#080808"       # Deep black card surface
    BG_CARD_HOVER = "#121212" # Black card hover state
    BG_INPUT = "#0A0A0A"      # Deep black input surface
    BG_GLASS_PILL = "#0D0D0D" # Dark pill surface

    # Black Borders
    BORDER = "#141414"        # Subtle black border
    BORDER_GLOW = "#222222"   # Deep dark border highlight
    BORDER_CYAN = "#0066FF"   # Blue accent border

    # Buttons & Accents (Vibrant Blue)
    PRIMARY = "#0066FF"       # Strong electric blue for buttons
    PRIMARY_HOVER = "#1A75FF" # Hover blue
    BTN_SECONDARY = "#0047B3" # Medium blue for secondary buttons
    BTN_SECONDARY_HOVER = "#005CE6" # Secondary button hover
    SUCCESS = "#10B981"       # Status indicator green
    WARNING = "#F59E0B"       # Status indicator amber
    ERROR = "#EF4444"         # Status indicator red

    # Typography (Pure Crisp White)
    TEXT_PRIMARY = "#FFFFFF"   # White text
    TEXT_SECONDARY = "#E5E5E5" # Soft white for secondary labels
    TEXT_MUTED = "#888888"     # Muted gray-white text

    # Fonts (Safe standard Windows fonts)
    FONT_FAMILY = "Segoe UI"
    FONT_TITLE = ("Segoe UI", 18, "bold")
    FONT_SUBTITLE = ("Segoe UI", 14, "bold")
    FONT_BODY = ("Segoe UI", 12)
    FONT_BODY_BOLD = ("Segoe UI", 12, "bold")
    FONT_SMALL = ("Segoe UI", 10)
    FONT_MONO = ("Consolas", 10)

