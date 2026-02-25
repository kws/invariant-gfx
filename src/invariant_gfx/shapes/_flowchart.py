"""Flowchart convenience shapes (polygon wrappers)."""

from __future__ import annotations

from decimal import Decimal

from invariant_gfx.shapes._primitives import polygon
from invariant_gfx.shapes._svg import (
    _color_attrs,
    _embed,
    _expr_half,
    _wrap_svg,
)


def diamond(
    width: int | Decimal | str,
    height: int | Decimal | str,
    *,
    cx: int | Decimal | str | None = None,
    cy: int | Decimal | str | None = None,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int] | None = None,
    stroke_width: int = 0,
) -> str:
    """Create an SVG diamond (rotated square) shape.

    Args:
        width: Diamond width
        height: Diamond height
        cx: Center X (defaults to width/2)
        cy: Center Y (defaults to height/2)
        fill: RGBA fill color
        stroke: Optional stroke color
        stroke_width: Stroke width

    Returns:
        Complete SVG string with viewBox.
    """
    half_w = _expr_half(width)
    half_h = _expr_half(height)
    if cx is None and cy is None:
        points_str = (
            f"{half_w},0 {_embed(width)},{half_h} {half_w},{_embed(height)} 0,{half_h}"
        )
    else:
        cx_val = _embed(cx) if cx is not None else half_w
        cy_val = _embed(cy) if cy is not None else half_h
        points_str = (
            f"{cx_val},({cy_val} - {half_h}) "
            f"({cx_val} + {half_w}),{cy_val} "
            f"{cx_val},({cy_val} + {half_h}) "
            f"({cx_val} - {half_w}),{cy_val}"
        )
    attrs = _color_attrs(fill, stroke, stroke_width)
    content = f'<polygon points="{points_str}" {attrs} />'
    return _wrap_svg(_embed(width), _embed(height), content)


def parallelogram(
    width: int | Decimal | str,
    height: int | Decimal | str,
    *,
    skew: int | Decimal = 0,
    x: int | Decimal | str = 0,
    y: int | Decimal | str = 0,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int] | None = None,
    stroke_width: int = 0,
) -> str:
    """Create an SVG parallelogram.

    Args:
        width: Parallelogram width
        height: Parallelogram height
        skew: Horizontal skew as fraction of width (0-1, e.g. 0.2 for 20%)
        x: X offset
        y: Y offset
        fill: RGBA fill color
        stroke: Optional stroke color
        stroke_width: Stroke width

    Returns:
        Complete SVG string with viewBox.
    """
    if all(isinstance(v, (int, Decimal)) for v in (width, height, x, y, skew)):
        w, h = int(width), int(height)
        x_i, y_i = int(x), int(y)
        s = int(Decimal(str(skew)) * w) if isinstance(skew, (int, Decimal)) else 0
        s = min(max(0, s), w - 1)
        points = [
            (x_i + s, y_i),
            (x_i + w, y_i),
            (x_i + w - s, y_i + h),
            (x_i, y_i + h),
        ]
        return polygon(
            points,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width,
        )
    x_str = _embed(x)
    y_str = _embed(y)
    w_str = _embed(width)
    h_str = _embed(height)
    skew_str = _embed(skew)
    s_expr = f"({skew_str} * {w_str})"
    points_str = (
        f"({x_str} + {s_expr}),{y_str} "
        f"({x_str} + {w_str}),{y_str} "
        f"({x_str} + {w_str} - {s_expr}),({y_str} + {h_str}) "
        f"{x_str},({y_str} + {h_str})"
    )
    attrs = _color_attrs(fill, stroke, stroke_width)
    content = f'<polygon points="{points_str}" {attrs} />'
    return _wrap_svg(_embed(width), _embed(height), content)


def hexagon(
    width: int | Decimal | str,
    height: int | Decimal | str,
    *,
    flat_top: bool = True,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int] | None = None,
    stroke_width: int = 0,
) -> str:
    """Create an SVG hexagon.

    Args:
        width: Hexagon width
        height: Hexagon height
        flat_top: If True, horizontal top edge; else pointy top
        fill: RGBA fill color
        stroke: Optional stroke color
        stroke_width: Stroke width

    Returns:
        Complete SVG string with viewBox.
    """
    if all(isinstance(v, (int, Decimal)) for v in (width, height)):
        w, h = int(width), int(height)
        h4 = h // 4
        h34 = 3 * h // 4
        w2 = w // 2
        if flat_top:
            points = [
                (w2, 0),
                (w, h4),
                (w, h34),
                (w2, h),
                (0, h34),
                (0, h4),
            ]
        else:
            points = [
                (w4 := w // 4, 0),
                (3 * w4, 0),
                (w, h2 := h // 2),
                (3 * w4, h),
                (w4, h),
                (0, h2),
            ]
        return polygon(
            points,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width,
        )
    half_w = _expr_half(width)
    quarter_h = f"({_embed(height)} / 4)"
    three_quarter_h = f"({_embed(height)} * 3 / 4)"
    half_h = _expr_half(height)
    quarter_w = f"({_embed(width)} / 4)"
    three_quarter_w = f"({_embed(width)} * 3 / 4)"
    if flat_top:
        points_str = (
            f"{half_w},0 "
            f"{_embed(width)},{quarter_h} "
            f"{_embed(width)},{three_quarter_h} "
            f"{half_w},{_embed(height)} "
            f"0,{three_quarter_h} "
            f"0,{quarter_h}"
        )
    else:
        points_str = (
            f"{quarter_w},0 "
            f"{three_quarter_w},0 "
            f"{_embed(width)},{half_h} "
            f"{three_quarter_w},{_embed(height)} "
            f"{quarter_w},{_embed(height)} "
            f"0,{half_h}"
        )
    attrs = _color_attrs(fill, stroke, stroke_width)
    content = f'<polygon points="{points_str}" {attrs} />'
    return _wrap_svg(_embed(width), _embed(height), content)
