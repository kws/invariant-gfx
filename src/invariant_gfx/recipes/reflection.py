"""Reflection effect recipe: pad (when skew), flip, squash, quad, gradient, gap, crop_to_content.

Produces a faded mirror of the source below it. Uses gradient opacity (opaque at
top near the text, transparent at bottom) for a natural surface reflection.
When skew > 0: pads horizontally so the quad perspective has room to expand,
then crop_to_content trims only fully transparent regions (keeps gradient fade
and expanded content). Squash compresses vertically; skew uses quad transform
(top fixed, bottom tilts). When gap > 0, translates down (dy only). Composite
with anchor "cs@ce" to center the reflection below.
"""

from decimal import Decimal

from invariant import Node, SubGraphNode, ref


def reflection(
    source: str,
    *,
    angle: Decimal | int = 90,
    gradient_start: Decimal = Decimal("0.8"),
    gradient_end: Decimal = Decimal("0"),
    gradient_start_pos: Decimal = Decimal("0"),
    gradient_end_pos: Decimal = Decimal("0.5"),
    gap: int = 0,
    squash: Decimal | int = 1,
    skew: Decimal | int = 0,
) -> SubGraphNode:
    """Build a SubGraphNode that produces a reflection of a source image.

    The internal graph: (optional pad when skew > 0) -> flip -> (optional
    resize for squash) -> (optional quad when skew > 0) -> gradient_opacity ->
    (optional translate when gap > 0) -> (optional crop_to_content when skew > 0).
    Gradient opacity fades from top to bottom. Squash < 1 compresses the
    reflection vertically (e.g. 0.5 = half height) for a perspective effect.
    Skew applies horizontal shear for a subtle tilt. Translate uses dx=0 only.

    Args:
        source: Node ID of the source image (becomes the subgraph's dependency).
        angle: Gradient direction in degrees. Default 90 (top→bottom).
        gradient_start: Opacity (0-1) at top of reflection. Default 0.8.
        gradient_end: Opacity (0-1) at bottom of reflection. Default 0.
        gradient_start_pos: Position (0-1) where gradient begins. Default 0.
        gradient_end_pos: Position (0-1) where gradient ends. Default 0.5
            (PowerPoint-style: fade out halfway through).
        gap: Pixels between source and reflection. When > 0, translates the
            flipped image down (dy=gap, dx=0). Default 0.
        squash: Vertical compression factor (0-1). 1 = no squash, 0.5 = half
            height. Default 1.
        skew: Horizontal shear factor for tilt (e.g. 0.05 for subtle). Default 0.

    Returns:
        SubGraphNode with deps=[source], to be placed in the parent graph.
    """
    nodes: dict[str, Node] = {}
    subgraph_params: dict = {"source": ref(source)}

    # When skew > 0, pad horizontally so the quad perspective has room to expand.
    skew_dec = Decimal(str(skew))
    if skew_dec > 0:
        subgraph_params["skew"] = skew_dec
        pad_x = "${int(decimal(source.width) * skew)}"
        nodes["padded"] = Node(
            op_name="gfx:pad",
            params={
                "image": ref("source"),
                "left": pad_x,
                "top": 0,
                "right": pad_x,
                "bottom": 0,
            },
            deps=["source", "skew"],
        )
        base = "padded"
    else:
        base = "source"

    nodes["flipped"] = Node(
        op_name="gfx:flip",
        params={"image": ref(base), "horizontal": False, "vertical": True},
        deps=[base],
    )
    prev = "flipped"

    squash_dec = Decimal(str(squash))
    if squash_dec < 1:
        subgraph_params["squash"] = squash_dec
        nodes["squashed"] = Node(
            op_name="gfx:resize",
            params={
                "image": ref(prev),
                "width": f"${{{base}.width}}",
                "height": f"${{int(decimal({base}.height) * squash)}}",
            },
            deps=[prev, base, "squash"],
        )
        prev = "squashed"

    if skew_dec != 0:
        subgraph_params["skew"] = skew_dec
        # Quad: top edge fixed (meets source), bottom corners shift inward for perspective.
        # Corners: upper-left, lower-left, lower-right, upper-right.
        # Use list (not tuple) so resolve_params recurses and evaluates CEL.
        transform_input = prev
        nodes["perspective"] = Node(
            op_name="gfx:transform",
            params={
                "image": ref(transform_input),
                "method": "quad",
                "data": [
                    0,
                    0,
                    f"${{int(decimal({transform_input}.width) * skew)}}",
                    f"${{{transform_input}.height}}",
                    f"${{{transform_input}.width - int(decimal({transform_input}.width) * skew)}}",
                    f"${{{transform_input}.height}}",
                    f"${{{transform_input}.width}}",
                    0,
                ],
                "size": [
                    f"${{{transform_input}.width}}",
                    f"${{{transform_input}.height}}",
                ],
            },
            deps=[transform_input, "skew"],
        )
        prev = "perspective"

    nodes["faded"] = Node(
        op_name="gfx:gradient_opacity",
        params={
            "image": ref(prev),
            "angle": angle,
            "start": gradient_start,
            "end": gradient_end,
            "start_pos": gradient_start_pos,
            "end_pos": gradient_end_pos,
        },
        deps=[prev],
    )
    prev = "faded"

    if gap > 0:
        nodes["offset"] = Node(
            op_name="gfx:translate",
            params={"image": ref(prev), "dx": 0, "dy": gap},
            deps=[prev],
        )
        prev = "offset"

    # When we padded for skew, trim only fully transparent regions (keeps gradient
    # fade and any content that expanded into the padded area).
    if skew_dec > 0:
        nodes["trimmed"] = Node(
            op_name="gfx:crop_to_content",
            params={"image": ref(prev)},
            deps=[prev],
        )
        prev = "trimmed"

    return SubGraphNode(
        params=subgraph_params,
        deps=[source],
        graph=nodes,
        output=prev,
    )
