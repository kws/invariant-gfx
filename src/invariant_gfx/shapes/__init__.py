"""Composable SVG shape builders for use with gfx:render_svg."""

from invariant_gfx.shapes._chart import arrow
from invariant_gfx.shapes._flowchart import diamond, hexagon, parallelogram
from invariant_gfx.shapes._primitives import (
    arc,
    circle,
    ellipse,
    line,
    polygon,
    rect,
    rounded_rect,
)

__all__ = [
    "arc",
    "arrow",
    "circle",
    "diamond",
    "ellipse",
    "hexagon",
    "line",
    "parallelogram",
    "polygon",
    "rect",
    "rounded_rect",
]
