"""Internal SVG utilities for shape builders."""

from __future__ import annotations

from decimal import Decimal


def _embed(value: int | Decimal | str) -> str:
    """Return value as string for embedding. Expressions passed through."""
    if isinstance(value, str):
        return value  # CEL expression
    return str(value)


def _expr_half(value: int | Decimal | str) -> str:
    """Return expression for value/2. For CEL strings, wraps in parentheses for correct precedence."""
    if isinstance(value, str):
        return f"({value})/2"  # e.g. "(${text.width + 24})/2"
    return str(int(value) // 2)


def _expr_add(a: int | Decimal | str, b: int | Decimal | str) -> str:
    """Return expression for a+b. For CEL strings, wraps in parentheses."""
    if isinstance(a, (int, Decimal)) and int(a) == 0:
        return _embed(b)
    if isinstance(b, (int, Decimal)) and int(b) == 0:
        return _embed(a)
    a_str = _embed(a)
    b_str = _embed(b)
    if isinstance(a, str) or isinstance(b, str):
        return f"({a_str} + {b_str})"
    return str(int(a) + int(b))


def _expr_sub(a: int | Decimal | str, b: int | Decimal | str) -> str:
    """Return expression for a-b. For CEL strings, wraps in parentheses."""
    if isinstance(b, (int, Decimal)) and int(b) == 0:
        return _embed(a)
    a_str = _embed(a)
    b_str = _embed(b)
    if isinstance(a, str) or isinstance(b, str):
        return f"({a_str} - {b_str})"
    return str(int(a) - int(b))


def _color_attrs(
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int] | None,
    stroke_width: int,
) -> str:
    """Produce fill/stroke attributes. Returns space-separated attr string."""
    fill_hex = f"#{fill[0]:02x}{fill[1]:02x}{fill[2]:02x}"
    fill_opacity = fill[3] / 255.0
    attrs = [f'fill="{fill_hex}"', f'fill-opacity="{fill_opacity}"']
    if stroke is not None and stroke_width > 0:
        stroke_hex = f"#{stroke[0]:02x}{stroke[1]:02x}{stroke[2]:02x}"
        stroke_opacity = stroke[3] / 255.0
        attrs.extend(
            [
                f'stroke="{stroke_hex}"',
                f'stroke-opacity="{stroke_opacity}"',
                f'stroke-width="{stroke_width}"',
            ]
        )
    return " ".join(attrs)


def _wrap_svg(viewbox_w: str, viewbox_h: str, content: str) -> str:
    """Wrap content in SVG root element with viewBox 0 0 w h."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {viewbox_w} {viewbox_h}">\n'
        f"  {content}\n"
        f"</svg>"
    )


def _wrap_svg_viewbox(
    min_x: str, min_y: str, width: str, height: str, content: str
) -> str:
    """Wrap content in SVG root element with viewBox minX minY width height."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{min_x} {min_y} {width} {height}">\n'
        f"  {content}\n"
        f"</svg>"
    )
