"""Inner glow effect recipe: extract alpha, pad, invert, blur, colorize, mask.

Same as inner_shadow but no translate, bright color. Composite above source
with mode="screen" or "add" for luminosity.
"""

from decimal import ROUND_CEILING, Decimal

from invariant import Node, SubGraphNode, ref


def inner_glow(
    source: str,
    *,
    radius: int = 0,
    sigma: Decimal = Decimal("3"),
    color: tuple[int, int, int, int] = (255, 255, 200, 180),
) -> SubGraphNode:
    """Build a SubGraphNode that produces an inner glow from a source image.

    The internal graph: extract_alpha -> pad -> invert_alpha -> (optional
    dilate) -> gaussian_blur -> colorize -> mask_alpha. No translate.

    Args:
        source: Node ID of the source image (becomes the subgraph's dependency).
        radius: Spread radius before blur. Default 0.
        sigma: Blur standard deviation. Default Decimal("3").
        color: Glow color (RGBA 0-255). Default (255, 255, 200, 180).

    Returns:
        SubGraphNode with deps=[source], to be placed in the parent graph.
    """
    nodes: dict[str, Node] = {}

    nodes["alpha"] = Node(
        op_name="gfx:extract_alpha",
        params={"image": ref("source")},
        deps=["source"],
    )

    pad = int((Decimal("3") * sigma).to_integral_value(rounding=ROUND_CEILING)) + radius
    nodes["padded"] = Node(
        op_name="gfx:pad",
        params={
            "image": ref("alpha"),
            "left": pad,
            "top": pad,
            "right": pad,
            "bottom": pad,
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

    nodes["clipped"] = Node(
        op_name="gfx:mask_alpha",
        params={"image": ref(prev), "mask": ref("padded")},
        deps=[prev, "padded"],
    )

    return SubGraphNode(
        params={"source": ref(source)},
        deps=[source],
        graph=nodes,
        output="clipped",
    )
