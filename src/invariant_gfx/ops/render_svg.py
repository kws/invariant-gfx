"""gfx:render_svg operation - converts SVG blobs into raster artifacts using cairosvg."""

from decimal import Decimal
from io import BytesIO
from typing import Any

import cairosvg
from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import BlobArtifact, ImageArtifact


def render_svg(manifest: dict[str, Any]) -> ICacheable:
    """Convert SVG blobs into raster artifacts using cairosvg.

    Args:
        manifest: Must contain:
            - Upstream BlobArtifact (SVG content, accessed via dependency ID)
            - 'width': Decimal (target raster width in pixels)
            - 'height': Decimal (target raster height in pixels)

    Returns:
        ImageArtifact with rasterized SVG (RGBA mode).

    Raises:
        KeyError: If required keys are missing.
        ValueError: If SVG cannot be rendered or dimensions are invalid.
    """
    if "width" not in manifest:
        raise KeyError("gfx:render_svg requires 'width' in manifest")
    if "height" not in manifest:
        raise KeyError("gfx:render_svg requires 'height' in manifest")

    width_val = manifest["width"]
    height_val = manifest["height"]

    # Convert to int (handles Decimal, int, or string)
    if isinstance(width_val, Decimal):
        width = int(width_val)
    elif isinstance(width_val, (int, str)):
        width = int(width_val)
    else:
        raise ValueError(f"width must be Decimal, int, or str, got {type(width_val)}")

    if isinstance(height_val, Decimal):
        height = int(height_val)
    elif isinstance(height_val, (int, str)):
        height = int(height_val)
    else:
        raise ValueError(f"height must be Decimal, int, or str, got {type(height_val)}")

    if width <= 0 or height <= 0:
        raise ValueError(f"size must be positive, got {width}x{height}")

    # Find the upstream BlobArtifact
    known_params = {"width", "height"}
    svg_blob = None
    for key, value in manifest.items():
        if key not in known_params and isinstance(value, BlobArtifact):
            if svg_blob is not None:
                raise ValueError(
                    "gfx:render_svg found multiple BlobArtifacts in manifest. "
                    "render_svg expects exactly one upstream dependency."
                )
            svg_blob = value

    if svg_blob is None:
        raise KeyError(
            "gfx:render_svg requires an upstream BlobArtifact in manifest. "
            "Make sure the source node is listed in deps."
        )

    # Verify it's SVG (be lenient - some SVG resources might not have exact content type)
    # We'll try to render it anyway

    # Render SVG to PNG using cairosvg
    try:
        png_bytes = cairosvg.svg2png(
            bytestring=svg_blob.data,
            output_width=width,
            output_height=height,
        )
    except Exception as e:
        raise ValueError(f"gfx:render_svg failed to render SVG: {e}") from e

    # Parse PNG into PIL Image
    try:
        image = Image.open(BytesIO(png_bytes))
        # Convert to RGBA mode
        if image.mode != "RGBA":
            image = image.convert("RGBA")
    except Exception as e:
        raise ValueError(f"gfx:render_svg failed to parse rendered PNG: {e}") from e

    return ImageArtifact(image)
