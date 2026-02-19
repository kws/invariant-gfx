"""Anchor functions for layer positioning in composite operations."""

from decimal import Decimal
from typing import Any


def absolute(x: int | Decimal | str, y: int | Decimal | str) -> dict[str, Any]:
    """Place a layer at absolute pixel coordinates on the canvas.

    Args:
        x: Pixel offset from left edge. Can be int, Decimal, or str (for CEL expressions).
        y: Pixel offset from top edge. Can be int, Decimal, or str (for CEL expressions).

    Returns:
        Dictionary with anchor specification for use in composite layers.
    """
    return {
        "type": "absolute",
        "x": x,
        "y": y,
    }


def relative(
    parent: str,
    align: str,
    x: int | Decimal | str = 0,
    y: int | Decimal | str = 0,
) -> dict[str, Any]:
    """Position a layer relative to a previously-placed layer.

    Args:
        parent: Dependency ID of the layer to position relative to.
        align: Alignment string (e.g., "c,c" for center-center, "se,se" for start-end).
               Format: comma-separated pair where first value = self alignment,
               second value = parent alignment. Each value can be:
               - "s" (start), "c" (center), "e" (end) for single-axis
               - "se", "ce", "ee", etc. for two-axis (x,y)
        x: Optional horizontal offset in pixels (default 0). Can be int, Decimal, or str.
        y: Optional vertical offset in pixels (default 0). Can be int, Decimal, or str.

    Returns:
        Dictionary with anchor specification for use in composite layers.
    """
    return {
        "type": "relative",
        "parent": parent,
        "align": align,
        "x": x,
        "y": y,
    }
