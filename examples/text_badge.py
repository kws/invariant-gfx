#!/usr/bin/env python3
"""Example: Text Badge Pipeline — In-Flight SVG Modification

This example demonstrates that invariant_gfx can modify SVG content "in-flight"
using CEL expression interpolation. The SVG badge template contains ${...}
expressions that reference upstream artifact dimensions, which are resolved during
Phase 1 (Context Resolution) before the SVG is rendered.

The key insight: the SVG badge is a template string with embedded expressions
like ${text.width + 24} and ${text.height + 16}. The pipeline measures the text
first, then resolves these expressions to produce a concrete SVG with viewBox
and dimensions that perfectly fit the content. Because the SVG coordinate system
matches the pixel dimensions 1:1, rounded corners remain undistorted at any
aspect ratio.

Usage:
    poetry run python examples/text_badge.py
    poetry run python examples/text_badge.py --text "Hello"
    poetry run python examples/text_badge.py --text "42" --font-size 24 --bg-color 200,0,0
"""

import argparse
from decimal import Decimal
from pathlib import Path

from invariant import Executor, Node, ref
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore

from invariant_gfx import register_core_ops
from invariant_gfx.anchors import relative


def parse_rgba(color_str: str) -> tuple[int, int, int, int]:
    """Parse RGBA color string into tuple.

    Format: "R,G,B" or "R,G,B,A" (0-255 per channel, A defaults to 255).

    Args:
        color_str: Color string

    Returns:
        RGBA tuple (r, g, b, a).
    """
    parts = color_str.split(",")
    if len(parts) == 3:
        r, g, b = [int(p.strip()) for p in parts]
        return (r, g, b, 255)
    elif len(parts) == 4:
        r, g, b, a = [int(p.strip()) for p in parts]
        return (r, g, b, a)
    else:
        raise ValueError(
            f"Invalid color format: {color_str}. Expected 'R,G,B' or 'R,G,B,A'"
        )


def create_badge_svg_template(
    corner_radius: int = 8,
    fill_color: tuple[int, int, int, int] = (50, 50, 50, 255),
    border_color: tuple[int, int, int, int] | None = None,
    border_width: int = 1,
    padding_x: int = 12,
    padding_y: int = 8,
) -> str:
    """Generate SVG template for a rounded rectangle badge with dynamic dimensions.

    The SVG template contains ${...} CEL expressions that reference upstream
    artifact dimensions (e.g., ${text.width + 24}). These expressions are
    resolved during Phase 1 (Context Resolution) before the SVG is rendered,
    producing a concrete SVG with viewBox and dimensions that perfectly fit
    the content.

    Because the SVG coordinate system matches pixel dimensions 1:1 (no stretching),
    rounded corners remain undistorted at any aspect ratio.

    Args:
        corner_radius: Corner radius in pixels
        fill_color: Background fill color (RGBA)
        border_color: Optional border color (RGBA), defaults to darker fill
        border_width: Border width in pixels
        padding_x: Horizontal padding (used in expressions)
        padding_y: Vertical padding (used in expressions)

    Returns:
        SVG XML template string with ${...} expressions.
    """
    if border_color is None:
        # Darker version of fill color
        border_color = (
            max(0, fill_color[0] - 30),
            max(0, fill_color[1] - 30),
            max(0, fill_color[2] - 30),
            fill_color[3],
        )

    # Convert RGBA to hex (ignoring alpha for fill/stroke, using opacity)
    fill_hex = f"#{fill_color[0]:02x}{fill_color[1]:02x}{fill_color[2]:02x}"
    border_hex = f"#{border_color[0]:02x}{border_color[1]:02x}{border_color[2]:02x}"
    fill_opacity = fill_color[3] / 255.0
    border_opacity = border_color[3] / 255.0

    # Calculate total dimensions with padding
    padding_x_total = padding_x * 2
    padding_y_total = padding_y * 2

    # SVG template with ${...} expressions that will be resolved in-flight
    # The expressions reference the "text" dependency's width/height properties
    svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${{text.width + {padding_x_total}}} ${{text.height + {padding_y_total}}}">
  <rect
    x="{border_width}"
    y="{border_width}"
    width="${{text.width + {padding_x_total - 2 * border_width}}}"
    height="${{text.height + {padding_y_total - 2 * border_width}}}"
    rx="{corner_radius}"
    ry="{corner_radius}"
    fill="{fill_hex}"
    fill-opacity="{fill_opacity}"
    stroke="{border_hex}"
    stroke-opacity="{border_opacity}"
    stroke-width="{border_width}"
  />
</svg>"""
    return svg_template


def create_badge_graph(
    text: str,
    font: str,
    font_size: Decimal,
    text_color: tuple[int, int, int, int],
    bg_color: tuple[int, int, int, int],
    border_color: tuple[int, int, int, int] | None,
    padding_x: int,
    padding_y: int,
) -> dict:
    """Create the text badge graph.

    Args:
        text: Text to display
        font: Font family name
        font_size: Font size in points
        text_color: Text color (RGBA)
        bg_color: Badge background color (RGBA)
        border_color: Optional border color (RGBA)
        padding_x: Horizontal padding around text (pixels)
        padding_y: Vertical padding around text (pixels)

    Returns:
        Graph dictionary.
    """
    # Generate SVG template with ${...} expressions (resolved in-flight)
    badge_svg_template = create_badge_svg_template(
        corner_radius=8,
        fill_color=bg_color,
        border_color=border_color,
        border_width=1,
        padding_x=padding_x,
        padding_y=padding_y,
    )

    graph = {
        # Render text first to get its dimensions
        "text": Node(
            op_name="gfx:render_text",
            params={
                "text": text,
                "font": font,
                "size": font_size,
                "color": text_color,
            },
            deps=[],
        ),
        # Render badge SVG: template expressions resolved before rendering
        "badge": Node(
            op_name="gfx:render_svg",
            params={
                "svg_content": badge_svg_template,  # Contains ${...} expressions
                "width": f"${{text.width + {padding_x * 2}}}",  # Text width + padding
                "height": f"${{text.height + {padding_y * 2}}}",  # Text height + padding
            },
            deps=["text"],
        ),
        # Composite: badge on bottom, text centered on top
        "final": Node(
            op_name="gfx:composite",
            params={
                "layers": [
                    {
                        "image": ref("badge"),
                        "id": "badge",
                    },
                    {
                        "image": ref("text"),
                        "anchor": relative("badge", "c@c"),
                        "id": "text",
                    },
                ],
            },
            deps=["badge", "text"],
        ),
    }

    return graph


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a text badge image using invariant_gfx pipeline"
    )
    parser.add_argument(
        "--text",
        type=str,
        default="Hello",
        help='Text to display (default: "Hello")',
    )
    parser.add_argument(
        "--font",
        type=str,
        default="Geneva",
        help='Font family name (default: "Geneva")',
    )
    parser.add_argument(
        "--font-size",
        type=int,
        default=14,
        help="Font size in points (default: 14)",
    )
    parser.add_argument(
        "--text-color",
        type=str,
        default="255,255,255",
        help='Text color as "R,G,B" or "R,G,B,A" (default: "255,255,255")',
    )
    parser.add_argument(
        "--bg-color",
        type=str,
        default="50,50,50",
        help='Background color as "R,G,B" or "R,G,B,A" (default: "50,50,50")',
    )
    parser.add_argument(
        "--border-color",
        type=str,
        default=None,
        help='Border color as "R,G,B" or "R,G,B,A" (default: darker version of bg-color)',
    )
    parser.add_argument(
        "--padding-x",
        type=int,
        default=12,
        help="Horizontal padding around text in pixels (default: 12)",
    )
    parser.add_argument(
        "--padding-y",
        type=int,
        default=8,
        help="Vertical padding around text in pixels (default: 8)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/badge.png",
        help="Output PNG file path (default: output/badge.png)",
    )

    args = parser.parse_args()

    # Parse colors
    try:
        text_color = parse_rgba(args.text_color)
        bg_color = parse_rgba(args.bg_color)
        border_color = parse_rgba(args.border_color) if args.border_color else None
    except ValueError as e:
        print(f"Error parsing color: {e}")
        return 1

    # Create graph
    graph = create_badge_graph(
        text=args.text,
        font=args.font,
        font_size=Decimal(str(args.font_size)),
        text_color=text_color,
        bg_color=bg_color,
        border_color=border_color,
        padding_x=args.padding_x,
        padding_y=args.padding_y,
    )

    # Setup executor
    registry = OpRegistry()
    registry.clear()
    register_core_ops(registry)

    store = MemoryStore()
    executor = Executor(registry=registry, store=store)

    # Execute graph
    print("Generating text badge...")
    print(f"  Text: {args.text}")
    print(f"  Font: {args.font} ({args.font_size}pt)")
    print(f"  Text color: {text_color}")
    print(f"  Background color: {bg_color}")
    if border_color:
        print(f"  Border color: {border_color}")
    print(f"  Padding: {args.padding_x}x{args.padding_y}")

    results = executor.execute(graph)

    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    final_image = results["final"].image
    final_image.save(output_path, format="PNG")

    print(f"\n✓ Saved to: {output_path}")
    print(f"  Dimensions: {final_image.width}x{final_image.height}")
    print(f"  Mode: {final_image.mode}")

    return 0


if __name__ == "__main__":
    exit(main())
