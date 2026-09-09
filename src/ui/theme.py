"""UI Theme and styling constants for GH-BOT-REPOS dark mode."""

from __future__ import annotations


class Theme:
    """Color palette and fonts for modern Windows Dark Mode."""

    # Glassmorphic Palette: Frosted Dark Glass + Obsidian + Electric Blue Specular
    BG_MAIN = "#06080E"
    BG_SIDEBAR = "#040508"
    BG_CARD = "#0C1322"
    BG_CARD_HOVER = "#121C30"
    BG_INPUT = "#080D17"
    BG_GLASS_PILL = "#10192A"

    # Glass Specular Edges (Refraction Borders)
    BORDER = "#1B2A42"
    BORDER_GLOW = "#25406B"
    BORDER_CYAN = "#00B4D8"

    # Accents (Strong Electric Blue & Neon Highlights)
    PRIMARY = "#0066FF"
    PRIMARY_HOVER = "#1A75FF"
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
