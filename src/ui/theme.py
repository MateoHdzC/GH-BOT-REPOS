"""UI Theme and styling constants for GH-BOT-REPOS dark mode."""

from __future__ import annotations


class Theme:
    """Color palette and fonts for modern Windows Glassmorphic Dark Mode."""

    # Glassmorphic Palette: Pure Deep Obsidian Black + Rich Midnight Navy Glass
    BG_MAIN = "#030712"       # Deep dark blue-black base
    BG_SIDEBAR = "#02040A"    # High-contrast pure dark obsidian
    BG_CARD = "#0B1528"       # Frosted deep electric midnight blue glass
    BG_CARD_HOVER = "#112240" # Illuminated glass hover state
    BG_INPUT = "#060D1A"      # Recessed input surface
    BG_GLASS_PILL = "#0E1E38" # Secondary interactive pill background

    # Glass Refraction Borders (Electric Specular Edges)
    BORDER = "#1E3A8A"        # Deep royal blue glass border (1px)
    BORDER_GLOW = "#2563EB"   # Active radiant electric blue border
    BORDER_CYAN = "#38BDF8"   # Subtle neon highlight

    # Accents (Strong Electric Blue & System Indicators)
    PRIMARY = "#0066FF"       # Vibrant strong electric blue (principal)
    PRIMARY_HOVER = "#1D4ED8" # Deep royal blue hover
    SUCCESS = "#10B981"       # Emerald green
    WARNING = "#F59E0B"       # Amber warning
    ERROR = "#EF4444"         # Radiant coral red

    # Typography
    TEXT_PRIMARY = "#FFFFFF"   # Pure crisp white for titles
    TEXT_SECONDARY = "#93C5FD" # Soft ice-blue tinted secondary text
    TEXT_MUTED = "#64748B"     # Slate muted text

    # Fonts (Safe standard Windows fonts)
    FONT_FAMILY = "Segoe UI"
    FONT_TITLE = ("Segoe UI", 18, "bold")
    FONT_SUBTITLE = ("Segoe UI", 14, "bold")
    FONT_BODY = ("Segoe UI", 12)
    FONT_BODY_BOLD = ("Segoe UI", 12, "bold")
    FONT_SMALL = ("Segoe UI", 10)
    FONT_MONO = ("Consolas", 10)

