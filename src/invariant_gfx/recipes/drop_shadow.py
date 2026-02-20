"""Drop-shadow effect recipe: extract alpha, optionally spread, blur, colorize, offset.

The output may extend beyond the source bounds (blur/translate). Padding the source
canvas (e.g. with gfx:pad) is the caller's responsibility if clipping must be avoided.
"""

from decimal import ROUND_CEILING, Decimal

from invariant import Node, SubGraphNode, ref


def drop_shadow(
    source: str,
    *,
    dx: int = 2,
    dy: int = 2,
    radius: int = 0,
    sigma: Decimal = Decimal("3"),
    color: tuple[int, int, int, int] = (0, 0, 0, 180),
) -> SubGraphNode:
    """Build a SubGraphNode that produces a drop shadow from a source image.

    The internal graph: extract_alpha -> pad -> (optional dilate) -> (optional
    gaussian_blur when sigma > 0) -> colorize -> (optional translate). The
    source image is passed in via context under the key "source" (SubGraphNode
    params/deps).

    Args:
        source: Node ID of the source image (becomes the subgraph's dependency).
        dx: Horizontal offset (positive = right). Default 2.
        dy: Vertical offset (positive = down). Default 2.
        radius: Spread radius (dilate before blur). Default 0.
        sigma: Blur standard deviation. Default Decimal("3").
        color: Shadow color (RGBA 0-255). Default (0, 0, 0, 180).

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
    prev = "padded"

    if radius > 0:
        nodes["dilated"] = Node(
            op_name="gfx:dilate",
            params={"image": ref(prev), "radius": radius},
            deps=[prev],
        )
        prev = "dilated"

    if sigma > 0:
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

    return SubGraphNode(
        params={"source": ref(source)},
        deps=[source],
        graph=nodes,
        output=prev,
    )
