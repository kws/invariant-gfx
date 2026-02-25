"""Inner shadow effect recipe: extract alpha, pad, invert, blur, colorize, offset, mask.

Creates a shadow visible only inside the source shape. Pad internally so blur
and translate do not clip. Composite above source with mode="multiply".
"""

from decimal import ROUND_CEILING, Decimal

from invariant import Node, SubGraphNode, ref


def inner_shadow(
    source: str,
    *,
    dx: int = 1,
    dy: int = 1,
    radius: int = 0,
    sigma: Decimal = Decimal("2"),
    color: tuple[int, int, int, int] = (0, 0, 0, 160),
) -> SubGraphNode:
    """Build a SubGraphNode that produces an inner shadow from a source image.

    The internal graph: extract_alpha -> pad -> invert_alpha -> (optional
    dilate) -> gaussian_blur -> colorize -> (optional translate) -> mask_alpha.
    The mask clips the effect to the interior of the source shape.

    Args:
        source: Node ID of the source image (becomes the subgraph's dependency).
        dx: Horizontal offset. Default 1.
        dy: Vertical offset. Default 1.
        radius: Spread radius before blur. Default 0.
        sigma: Blur standard deviation. Default Decimal("2").
        color: Shadow color (RGBA 0-255). Default (0, 0, 0, 160).

    Returns:
        SubGraphNode with deps=[source], to be placed in the parent graph.
    """
    nodes: dict[str, Node] = {}

    nodes["alpha"] = Node(
        op_name="gfx:extract_alpha",
        params={"image": ref("source")},
        deps=["source"],
    )

    pad_base = (
        int((Decimal("3") * sigma).to_integral_value(rounding=ROUND_CEILING)) + radius
    )
    nodes["padded"] = Node(
        op_name="gfx:pad",
        params={
            "image": ref("alpha"),
            "left": pad_base,
            "top": pad_base,
            "right": pad_base,
            "bottom": pad_base,
        },
        deps=["alpha"],
    )

    nodes["inverted"] = Node(
        op_name="gfx:invert_alpha",
        params={"image": ref("padded")},
        deps=["padded"],
    )
    prev = "inverted"

    if radius > 0:
        nodes["dilated"] = Node(
            op_name="gfx:dilate",
            params={"image": ref(prev), "radius": radius},
            deps=[prev],
        )
        prev = "dilated"

    nodes["blurred"] = Node(
        op_name="gfx:gaussian_blur",
        params={"image": ref(prev), "sigma": sigma},
        deps=[prev],
    )
    prev = "blurred"

    nodes["colored"] = Node(
        op_name="gfx:colorize",
        params={"image": ref(prev), "color": color},
        deps=[prev],
    )
    prev = "colored"

    if dx != 0 or dy != 0:
        nodes["offset"] = Node(
            op_name="gfx:translate",
            params={"image": ref(prev), "dx": dx, "dy": dy},
            deps=[prev],
        )
        prev = "offset"
        # Mask must match translate output size; pad the alpha by (dx, dy) on right/bottom
        nodes["mask_padded"] = Node(
            op_name="gfx:pad",
            params={
                "image": ref("padded"),
                "left": 0,
                "top": 0,
                "right": abs(dx),
                "bottom": abs(dy),
            },
            deps=["padded"],
        )
        mask_ref = "mask_padded"
    else:
        mask_ref = "padded"

    nodes["clipped"] = Node(
        op_name="gfx:mask_alpha",
        params={"image": ref(prev), "mask": ref(mask_ref)},
        deps=[prev, mask_ref],
    )

    return SubGraphNode(
        params={"source": ref(source)},
        deps=[source],
        graph=nodes,
        output="clipped",
    )
