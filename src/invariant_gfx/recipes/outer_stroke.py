"""Outer stroke effect recipe: extract alpha, pad, dilate, colorize.

Outlines the source silhouette with a solid-color border. Pads internally so
the stroke is not clipped at edges (gfx:dilate keeps canvas size).
"""

from invariant import Node, SubGraphNode, ref


def outer_stroke(
    source: str,
    *,
    width: int = 2,
    color: tuple[int, int, int, int] = (0, 0, 0, 255),
) -> SubGraphNode:
    """Build a SubGraphNode that produces an outer stroke around a source image.

    The internal graph: extract_alpha -> pad -> dilate -> colorize. The stroke
    is composited behind the source so the source covers the inner portion.

    Args:
        source: Node ID of the source image (becomes the subgraph's dependency).
        width: Stroke width in pixels. Default 2.
        color: Stroke color (RGBA 0-255). Default (0, 0, 0, 255).

    Returns:
        SubGraphNode with deps=[source], to be placed in the parent graph.
    """
    nodes: dict[str, Node] = {}

    nodes["alpha"] = Node(
        op_name="gfx:extract_alpha",
        params={"image": ref("source")},
        deps=["source"],
    )

    pad = width
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

    nodes["dilated"] = Node(
        op_name="gfx:dilate",
        params={"image": ref("padded"), "radius": width},
        deps=["padded"],
    )

    nodes["colored"] = Node(
        op_name="gfx:colorize",
        params={"image": ref("dilated"), "color": color},
        deps=["dilated"],
    )

    return SubGraphNode(
        params={"source": ref(source)},
        deps=[source],
        graph=nodes,
        output="colored",
    )
