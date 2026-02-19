"""gfx:resize operation - scales an ImageArtifact to target dimensions."""

from decimal import Decimal
from typing import Any

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def resize(manifest: dict[str, Any]) -> ICacheable:
    """Scale an ImageArtifact to target dimensions.

    Args:
        manifest: Must contain:
            - Upstream ImageArtifact (accessed via dependency ID)
            - 'width': Decimal (target width)
            - 'height': Decimal (target height)

    Returns:
        ImageArtifact with resized image (RGBA mode).

    Raises:
        KeyError: If required keys are missing.
        ValueError: If width/height values are invalid.
    """
    if "width" not in manifest:
        raise KeyError("gfx:resize requires 'width' in manifest")
    if "height" not in manifest:
        raise KeyError("gfx:resize requires 'height' in manifest")

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

    # Find the upstream ImageArtifact
    # The artifact is in the manifest keyed by its dependency ID
    # We look for ImageArtifact instances, excluding known parameter keys
    known_params = {"width", "height"}
    image_artifact = None
    for key, value in manifest.items():
        if key not in known_params and isinstance(value, ImageArtifact):
            if image_artifact is not None:
                raise ValueError(
                    "gfx:resize found multiple ImageArtifacts in manifest. "
                    "Resize expects exactly one upstream dependency."
                )
            image_artifact = value

    if image_artifact is None:
        raise KeyError(
            "gfx:resize requires an upstream ImageArtifact in manifest. "
            "Make sure the source node is listed in deps."
        )

    # Resize the image
    resized_image = image_artifact.image.resize(
        (width, height), Image.Resampling.LANCZOS
    )

    return ImageArtifact(resized_image)
