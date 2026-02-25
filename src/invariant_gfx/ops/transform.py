"""gfx:transform operation - thin wrapper around PIL Image.transform."""

from decimal import Decimal

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact

_TRANSFORM_METHODS = {
    "extent": Image.Transform.EXTENT,
    "affine": Image.Transform.AFFINE,
    "perspective": Image.Transform.PERSPECTIVE,
    "quad": Image.Transform.QUAD,
}


def _to_float(value: Decimal | int | str | float) -> float:
    """Convert value to float for PIL. Deterministic for given input."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, str):
        return float(value)
    raise ValueError(f"value must be Decimal, int, float, or str, got {type(value)}")


def _to_int(value: Decimal | int | str) -> int:
    """Convert value to int."""
    if isinstance(value, int):
        return value
    if isinstance(value, Decimal):
        return int(value)
    if isinstance(value, str):
        return int(value)
    raise ValueError(f"value must be Decimal, int, or str, got {type(value)}")


def transform(
    image: ImageArtifact,
    method: str,
    data: tuple | list,
    size: tuple,
) -> ICacheable:
    """Apply a PIL transform to an ImageArtifact.

    Thin wrapper around Image.transform(). Supports extent, affine,
    perspective, and quad methods. Use quad for perspective effects
    (e.g. reflection that "meets" the source with fixed top edge).

    Args:
        image: ImageArtifact (source image).
        method: One of "extent", "affine", "perspective", "quad".
        data: Method-specific coefficients. For quad: 8-tuple
            (x0,y0,x1,y1,x2,y2,x3,y3) = upper left, lower left,
            lower right, upper right corners of source quadrilateral.
        size: Output (width, height) in pixels.

    Returns:
        ImageArtifact with transformed content.

    Raises:
        ValueError: If image is not ImageArtifact, method invalid,
            or data/size have wrong length.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    method_lower = method.lower()
    if method_lower not in _TRANSFORM_METHODS:
        raise ValueError(
            f"method must be one of {list(_TRANSFORM_METHODS)}, got {method!r}"
        )

    pil_method = _TRANSFORM_METHODS[method_lower]

    # Convert data to tuple of floats
    data_seq = tuple(_to_float(v) for v in data)

    expected_len = {"extent": 4, "affine": 6, "perspective": 8, "quad": 8}
    if len(data_seq) != expected_len[method_lower]:
        raise ValueError(
            f"data for {method} must have {expected_len[method_lower]} values, "
            f"got {len(data_seq)}"
        )

    out_w = _to_int(size[0])
    out_h = _to_int(size[1])
    if out_w <= 0 or out_h <= 0:
        raise ValueError(f"size must be positive, got {out_w}x{out_h}")

    result = image.image.transform(
        (out_w, out_h),
        pil_method,
        data_seq,
        resample=Image.Resampling.BILINEAR,
        fillcolor=(0, 0, 0, 0),
    )
    return ImageArtifact(result)
