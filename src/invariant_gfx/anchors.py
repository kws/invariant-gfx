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
        parent: Layer ID (the 'id' field of a previously-listed layer) to position relative to.
        align: Alignment string (e.g., "c@c" for center-center, "se@es" for start-end).
               Format: "self@parent" where:
               - self and parent use 1-2 characters from 's' (start), 'c' (center), 'e' (end)
               - 1 character applies to both axes (e.g., "c" means "cc")
               - 2 characters: first is x-axis, second is y-axis
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
