"""gfx:gradient_opacity operation - applies a linear gradient to the alpha channel."""

import math
from decimal import Decimal

from PIL import Image, ImageChops

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def _to_float(value: Decimal | int | str) -> float:
    """Convert value to float for CEL compatibility."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, str)):
        return float(value)
    raise ValueError(f"value must be Decimal, int, or str, got {type(value)}")


def gradient_opacity(
    image: ImageArtifact,
    angle: Decimal | int | str,
    start: Decimal | int | str = Decimal("1"),
    end: Decimal | int | str = Decimal("0"),
    start_pos: Decimal | int | str = Decimal("0"),
    end_pos: Decimal | int | str = Decimal("1"),
) -> ICacheable:
    """Apply a linear gradient to the image's alpha channel.

    The gradient runs along the given angle (degrees). Angle 0 = left to right,
    90 = top to bottom. Start and end are opacity values (0 to 1) at the
    gradient's start and end points. start_pos and end_pos (0 to 1) control
    where the gradient runs within the image; outside that range, opacity is
    held at start or end respectively.

    Args:
        image: ImageArtifact (source image).
        angle: Gradient direction in degrees. 0 = left→right, 90 = top→bottom.
        start: Opacity (0-1) at the gradient start. Default 1.
        end: Opacity (0-1) at the gradient end. Default 0.
        start_pos: Position (0-1) where gradient begins. Default 0.
        end_pos: Position (0-1) where gradient ends. Default 1.

    Returns:
        ImageArtifact with RGB unchanged and alpha multiplied by the gradient.

    Raises:
        ValueError: If image is not an ImageArtifact or params are invalid.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    angle_rad = math.radians(_to_float(angle))
    start_val = _to_float(start)
    end_val = _to_float(end)
    start_pos_val = _to_float(start_pos)
    end_pos_val = _to_float(end_pos)

    if start_val < 0 or start_val > 1:
        raise ValueError(f"start must be in range 0 to 1, got {start_val}")
    if end_val < 0 or end_val > 1:
        raise ValueError(f"end must be in range 0 to 1, got {end_val}")
    if start_pos_val < 0 or start_pos_val > 1:
        raise ValueError(f"start_pos must be in range 0 to 1, got {start_pos_val}")
    if end_pos_val < 0 or end_pos_val > 1:
        raise ValueError(f"end_pos must be in range 0 to 1, got {end_pos_val}")
    if start_pos_val >= end_pos_val:
        raise ValueError(
            f"start_pos must be less than end_pos, got start_pos={start_pos_val} end_pos={end_pos_val}"
        )

    w = image.width
    h = image.height
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Build gradient mask: t = (px-0.5)*cos + (py-0.5)*sin + 0.5, clamp [0,1]
    # Remap t to factor: before start_pos use start_val, after end_pos use end_val,
    # between interpolate
    mask_data = []
    for y in range(h):
        py = (y + 0.5) / h
        for x in range(w):
            px = (x + 0.5) / w
            t = (px - 0.5) * cos_a + (py - 0.5) * sin_a + 0.5
            t = max(0.0, min(1.0, t))
            if t <= start_pos_val:
                factor = start_val
            elif t >= end_pos_val:
                factor = end_val
            else:
                t_local = (t - start_pos_val) / (end_pos_val - start_pos_val)
                factor = start_val + (end_val - start_val) * t_local
            mask_data.append(int(255 * factor))

    gradient_mask = Image.new("L", (w, h))
    gradient_mask.putdata(mask_data)

    r, g, b, a_in = image.image.split()
    a_out = ImageChops.multiply(a_in, gradient_mask)
    out = Image.merge("RGBA", (r, g, b, a_out))
    return ImageArtifact(out)
