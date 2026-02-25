"""Outer glow effect recipe: drop shadow with no offset and bright color.

Same pipeline as drop shadow (extract, pad, blur, colorize) but dx=dy=0.
Use mode="add" when compositing for best luminosity.
"""

from decimal import Decimal

from invariant import SubGraphNode

from invariant_gfx.recipes.drop_shadow import drop_shadow


def outer_glow(
    source: str,
    *,
    radius: int = 0,
    sigma: Decimal = Decimal("5"),
    color: tuple[int, int, int, int] = (255, 200, 0, 200),
) -> SubGraphNode:
    """Build a SubGraphNode that produces an outer glow around a source image.

    Wraps drop_shadow with dx=0, dy=0. Inherits internal pad from drop_shadow.
    Composite glow behind source; use mode="add" for best look.

    Args:
        source: Node ID of the source image (becomes the subgraph's dependency).
        radius: Spread radius before blur. Default 0.
        sigma: Blur standard deviation. Default Decimal("5").
        color: Glow color (RGBA 0-255). Default (255, 200, 0, 200).

    Returns:
        SubGraphNode with deps=[source], to be placed in the parent graph.
    """
    return drop_shadow(
        source,
        dx=0,
        dy=0,
        radius=radius,
        sigma=sigma,
        color=color,
    )
