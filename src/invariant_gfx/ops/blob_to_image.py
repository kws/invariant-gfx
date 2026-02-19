"""gfx:blob_to_image operation - parses raw binary data into ImageArtifact."""

from io import BytesIO
from typing import Any

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import BlobArtifact, ImageArtifact


def blob_to_image(manifest: dict[str, Any]) -> ICacheable:
    """Parse raw binary data (PNG, JPEG, WEBP) into ImageArtifact.

    Args:
        manifest: Must contain:
            - Upstream BlobArtifact (accessed via dependency ID)

    Returns:
        ImageArtifact with decoded image (RGBA mode).

    Raises:
        KeyError: If BlobArtifact is missing.
        ValueError: If blob data cannot be parsed as an image.
    """
    # Find the upstream BlobArtifact
    # The artifact is in the manifest keyed by its dependency ID
    blob_artifact = None
    for key, value in manifest.items():
        if isinstance(value, BlobArtifact):
            if blob_artifact is not None:
                raise ValueError(
                    "gfx:blob_to_image found multiple BlobArtifacts in manifest. "
                    "blob_to_image expects exactly one upstream dependency."
                )
            blob_artifact = value

    if blob_artifact is None:
        raise KeyError(
            "gfx:blob_to_image requires an upstream BlobArtifact in manifest. "
            "Make sure the source node is listed in deps."
        )

    # Parse the image from bytes
    try:
        image = Image.open(BytesIO(blob_artifact.data))
        # Convert to RGBA mode
        if image.mode != "RGBA":
            image = image.convert("RGBA")
    except Exception as e:
        raise ValueError(
            f"gfx:blob_to_image failed to parse image data: {e}. "
            f"Content type: {blob_artifact.content_type}"
        ) from e

    return ImageArtifact(image)
