"""Core SVG shape primitives for use with gfx:render_svg."""

from __future__ import annotations

import math
from decimal import Decimal

from invariant_gfx.shapes._svg import (
    _color_attrs,
    _embed,
    _expr_add,
    _expr_sub,
    _wrap_svg,
    _wrap_svg_viewbox,
)


def rect(
    width: int | Decimal | str,
    height: int | Decimal | str,
    *,
    x: int | Decimal | str = 0,
    y: int | Decimal | str = 0,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int] | None = None,
    stroke_width: int = 0,
) -> str:
    """Create an SVG rect shape.

    Args:
        width: Rectangle width
        height: Rectangle height
        x: X offset (default 0)
        y: Y offset (default 0)
        fill: RGBA fill color (0-255 per channel)
        stroke: Optional stroke color
        stroke_width: Stroke width (ignored when stroke is None)

    Returns:
        Complete SVG string with viewBox.
    """
    w = _embed(width)
    h = _embed(height)
    x_str = _embed(x)
    y_str = _embed(y)
    viewbox_w = _expr_add(x, width)
    viewbox_h = _expr_add(y, height)
    attrs = _color_attrs(fill, stroke, stroke_width)
    content = f'<rect x="{x_str}" y="{y_str}" width="{w}" height="{h}" {attrs} />'
    return _wrap_svg(viewbox_w, viewbox_h, content)


def rounded_rect(
    width: int | Decimal | str,
    height: int | Decimal | str,
    rx: int | Decimal,
    *,
    ry: int | Decimal | None = None,
    x: int | Decimal | str = 0,
    y: int | Decimal | str = 0,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int] | None = None,
    stroke_width: int = 0,
) -> str:
    """Create an SVG rounded rectangle.

    Args:
        width: Rectangle width
        height: Rectangle height
        rx: Corner radius X
        ry: Corner radius Y (defaults to rx)
        x: X offset (default 0)
        y: Y offset (default 0)
        fill: RGBA fill color
        stroke: Optional stroke color
        stroke_width: Stroke width

    Returns:
        Complete SVG string with viewBox.
    """
    ry_val = rx if ry is None else ry
    w = _embed(width)
    h = _embed(height)
    x_str = _embed(x)
    y_str = _embed(y)
    viewbox_w = _expr_add(x, width)
    viewbox_h = _expr_add(y, height)
    attrs = _color_attrs(fill, stroke, stroke_width)
    content = (
        f'<rect x="{x_str}" y="{y_str}" width="{w}" height="{h}" '
        f'rx="{rx}" ry="{ry_val}" {attrs} />'
    )
    return _wrap_svg(viewbox_w, viewbox_h, content)


def circle(
    cx: int | Decimal | str,
    cy: int | Decimal | str,
    r: int | Decimal | str,
    *,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int] | None = None,
    stroke_width: int = 0,
) -> str:
    """Create an SVG circle.

    Args:
        cx: Center X
        cy: Center Y
        r: Radius
        fill: RGBA fill color
        stroke: Optional stroke color
        stroke_width: Stroke width

    Returns:
        Complete SVG string with viewBox from circle bounding box.
    """
    r_str = _embed(r)
    viewbox_w = _expr_add(r, r)
    viewbox_h = viewbox_w
    min_x = _expr_sub(cx, r)
    min_y = _expr_sub(cy, r)
    attrs = _color_attrs(fill, stroke, stroke_width)
    content = f'<circle cx="{_embed(cx)}" cy="{_embed(cy)}" r="{r_str}" {attrs} />'
    return _wrap_svg_viewbox(min_x, min_y, viewbox_w, viewbox_h, content)


def ellipse(
    cx: int | Decimal | str,
    cy: int | Decimal | str,
    rx: int | Decimal | str,
    ry: int | Decimal | str,
    *,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int] | None = None,
    stroke_width: int = 0,
) -> str:
    """Create an SVG ellipse.

    Args:
        cx: Center X
        cy: Center Y
        rx: Radius X
        ry: Radius Y
        fill: RGBA fill color
        stroke: Optional stroke color
        stroke_width: Stroke width

    Returns:
        Complete SVG string with viewBox 0 0 2rx 2ry.
    """
    viewbox_w = _expr_add(rx, rx)
    viewbox_h = _expr_add(ry, ry)
    attrs = _color_attrs(fill, stroke, stroke_width)
    content = (
        f'<ellipse cx="{_embed(cx)}" cy="{_embed(cy)}" '
        f'rx="{_embed(rx)}" ry="{_embed(ry)}" {attrs} />'
    )
    return _wrap_svg(viewbox_w, viewbox_h, content)


def line(
    x1: int | Decimal | str,
    y1: int | Decimal | str,
    x2: int | Decimal | str,
    y2: int | Decimal | str,
    *,
    stroke: tuple[int, int, int, int],
    stroke_width: int = 1,
) -> str:
    """Create an SVG line.

    Args:
        x1: Start X
        y1: Start Y
        x2: End X
        y2: End Y
        stroke: Stroke color (required)
        stroke_width: Stroke width

    Returns:
        Complete SVG string with viewBox.
    """
    fill = (0, 0, 0, 0)  # Line has no fill
    attrs = _color_attrs(fill, stroke, stroke_width)
    content = (
        f'<line x1="{_embed(x1)}" y1="{_embed(y1)}" '
        f'x2="{_embed(x2)}" y2="{_embed(y2)}" {attrs} />'
    )
    if all(isinstance(v, (int, Decimal)) for v in (x1, y1, x2, y2)):
        x1_i, y1_i = int(x1), int(y1)
        x2_i, y2_i = int(x2), int(y2)
        min_x = min(x1_i, x2_i)
        min_y = min(y1_i, y2_i)
        vw = max(1, max(x1_i, x2_i) - min_x)
        vh = max(1, max(y1_i, y2_i) - min_y)
        return _wrap_svg_viewbox(str(min_x), str(min_y), str(vw), str(vh), content)
    viewbox_w = f"max({_embed(x1)}, {_embed(x2)})"
    viewbox_h = f"max({_embed(y1)}, {_embed(y2)})"
    return _wrap_svg(viewbox_w, viewbox_h, content)


def polygon(
    points: list[tuple[int, int]],
    *,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int] | None = None,
    stroke_width: int = 0,
) -> str:
    """Create an SVG polygon from literal points.

    Args:
        points: List of (x, y) coordinates (literal only)
        fill: RGBA fill color
        stroke: Optional stroke color
        stroke_width: Stroke width

    Returns:
        Complete SVG string with viewBox from points bbox.
    """
    if not points:
        raise ValueError("points must not be empty")
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    viewbox_w = max(1, max_x - min_x)
    viewbox_h = max(1, max_y - min_y)
    points_str = " ".join(f"{x},{y}" for x, y in points)
    attrs = _color_attrs(fill, stroke, stroke_width)
    content = f'<polygon points="{points_str}" {attrs} />'
    return _wrap_svg_viewbox(
        str(min_x), str(min_y), str(viewbox_w), str(viewbox_h), content
    )


def arc(
    cx: int | Decimal,
    cy: int | Decimal,
    r: int | Decimal | str,
    start_angle: int | Decimal,
    end_angle: int | Decimal,
    *,
    pie: bool = False,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int] | None = None,
    stroke_width: int = 0,
) -> str:
    """Create an SVG arc or pie slice.

    Args:
        cx: Center X
        cy: Center Y
        r: Radius
        start_angle: Start angle in degrees
        end_angle: End angle in degrees
        pie: If True, close as pie slice (filled)
        fill: RGBA fill color
        stroke: Optional stroke color
        stroke_width: Stroke width

    Returns:
        Complete SVG string with viewBox 0 0 2r 2r.
    """
    cx = int(cx)
    cy = int(cy)
    r_int = int(r) if not isinstance(r, str) else 0
    start_rad = math.radians(float(start_angle))
    end_rad = math.radians(float(end_angle))
    if isinstance(r, str):
        r_str = r
        min_x = f"({_embed(cx)} - {r})"
        min_y = f"({_embed(cy)} - {r})"
        viewbox_size = f"({r}) * 2"
    else:
        r_str = str(r_int)
        min_x = str(cx - r_int)
        min_y = str(cy - r_int)
        viewbox_size = str(2 * r_int)
    x1 = round(cx + r_int * math.cos(start_rad), 6)
    y1 = round(cy + r_int * math.sin(start_rad), 6)
    x2 = round(cx + r_int * math.cos(end_rad), 6)
    y2 = round(cy + r_int * math.sin(end_rad), 6)
    sweep = abs(end_rad - start_rad) > math.pi
    large_arc = 1 if sweep else 0
    # sweep_flag: 1 = clockwise (increasing angles), 0 = counter-clockwise
    # Use clockwise when end > start so arc goes from start to end
    sweep_flag = 1 if end_angle > start_angle else 0
    path_d = f"M {cx} {cy} L {x1} {y1} A {r_str} {r_str} 0 {large_arc} {sweep_flag} {x2} {y2}"
    if pie:
        path_d += " Z"
    attrs = _color_attrs(fill, stroke, stroke_width)
    content = f'<path d="{path_d}" {attrs} />'
    return _wrap_svg_viewbox(min_x, min_y, viewbox_size, viewbox_size, content)
