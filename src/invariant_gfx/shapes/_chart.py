"""Chart-oriented SVG shapes."""

from __future__ import annotations

import math
from decimal import Decimal

from invariant_gfx.shapes._svg import (
    _color_attrs,
    _embed,
    _wrap_svg,
    _wrap_svg_viewbox,
)


def arrow(
    x1: int | Decimal | str,
    y1: int | Decimal | str,
    x2: int | Decimal | str,
    y2: int | Decimal | str,
    *,
    stroke: tuple[int, int, int, int],
    stroke_width: int = 2,
    head_size: int | Decimal = 8,
    fill: tuple[int, int, int, int] | None = None,
) -> str:
    """Create an SVG arrow (line with arrowhead).

    Args:
        x1: Start X
        y1: Start Y
        x2: End X (arrow tip)
        y2: End Y (arrow tip)
        stroke: Stroke color
        stroke_width: Stroke width
        head_size: Arrowhead size in pixels
        fill: Arrowhead fill (defaults to stroke)

    Returns:
        Complete SVG string with viewBox.
    """
    fill_color = stroke if fill is None else fill
    line_attrs = _color_attrs((0, 0, 0, 0), stroke, stroke_width)
    head_attrs = _color_attrs(fill_color, stroke, stroke_width)

    if all(isinstance(v, (int, Decimal)) for v in (x1, y1, x2, y2, head_size)):
        x1_i, y1_i = int(x1), int(y1)
        x2_i, y2_i = int(x2), int(y2)
        hs = int(head_size)
        angle = math.atan2(y2_i - y1_i, x2_i - x1_i)
        head_angle = math.pi / 6
        xa = round(x2_i - hs * math.cos(angle - head_angle), 6)
        ya = round(y2_i - hs * math.sin(angle - head_angle), 6)
        xb = round(x2_i - hs * math.cos(angle + head_angle), 6)
        yb = round(y2_i - hs * math.sin(angle + head_angle), 6)
        path_d = f"M {xa} {ya} L {x2_i} {y2_i} L {xb} {yb} Z"
        line_el = (
            f'<line x1="{x1_i}" y1="{y1_i}" x2="{x2_i}" y2="{y2_i}" ' f"{line_attrs} />"
        )
        head_el = f'<path d="{path_d}" {head_attrs} />'
        content = f"{line_el}\n  {head_el}"
        min_x = min(x1_i, x2_i, int(xa), int(xb)) - 2
        min_y = min(y1_i, y2_i, int(ya), int(yb)) - 2
        max_x = max(x1_i, x2_i, int(xa), int(xb)) + 2
        max_y = max(y1_i, y2_i, int(ya), int(yb)) + 2
        vw = max(1, max_x - min_x)
        vh = max(1, max_y - min_y)
        return _wrap_svg_viewbox(str(min_x), str(min_y), str(vw), str(vh), content)
    line_el = (
        f'<line x1="{_embed(x1)}" y1="{_embed(y1)}" '
        f'x2="{_embed(x2)}" y2="{_embed(y2)}" {line_attrs} />'
    )
    viewbox_w = f"max({_embed(x1)}, {_embed(x2)}) + {int(head_size)}"
    viewbox_h = f"max({_embed(y1)}, {_embed(y2)}) + {int(head_size)}"
    return _wrap_svg(viewbox_w, viewbox_h, line_el)
