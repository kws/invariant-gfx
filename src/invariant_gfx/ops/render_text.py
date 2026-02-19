"""gfx:render_text operation - creates tight-fitting text artifacts using Pillow."""

from decimal import Decimal
from io import BytesIO
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from justmytype import get_default_registry

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import BlobArtifact, ImageArtifact


def render_text(manifest: dict[str, Any]) -> ICacheable:
    """Create a tight-fitting "Text Pill" artifact using Pillow.

    Args:
        manifest: Must contain:
            - 'text': String content to render
            - 'font': String (font family name) or BlobArtifact (font file bytes)
            - 'size': Decimal (font size in points)
            - 'color': Tuple[int, int, int, int] (RGBA, 0-255 per channel)
            - 'weight': int | None (font weight 100-900, optional, only for string fonts)
            - 'style': str (font style: "normal" or "italic", default "normal", only for string fonts)

    Returns:
        ImageArtifact sized to the text bounding box (RGBA mode).

    Raises:
        KeyError: If required keys are missing.
        ValueError: If font cannot be loaded or text cannot be rendered.
    """
    if "text" not in manifest:
        raise KeyError("gfx:render_text requires 'text' in manifest")
    if "font" not in manifest:
        raise KeyError("gfx:render_text requires 'font' in manifest")
    if "size" not in manifest:
        raise KeyError("gfx:render_text requires 'size' in manifest")
    if "color" not in manifest:
        raise KeyError("gfx:render_text requires 'color' in manifest")

    text = manifest["text"]
    if not isinstance(text, str):
        raise ValueError(f"text must be a string, got {type(text)}")

    font_spec = manifest["font"]
    size_val = manifest["size"]
    color = manifest["color"]

    # Convert size to int
    if isinstance(size_val, Decimal):
        size = int(size_val)
    elif isinstance(size_val, (int, str)):
        size = int(size_val)
    else:
        raise ValueError(f"size must be Decimal, int, or str, got {type(size_val)}")

    if size <= 0:
        raise ValueError(f"size must be positive, got {size}")

    # Validate color
    if not isinstance(color, (tuple, list)) or len(color) != 4:
        raise ValueError(
            f"color must be a tuple/list of 4 RGBA values, got {type(color)}"
        )

    r, g, b, a = color
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in (r, g, b, a)):
        raise ValueError(f"color values must be int in range 0-255, got {color}")

    # Load font
    if isinstance(font_spec, str):
        # String font name - resolve via JustMyType
        weight = manifest.get("weight")
        style = manifest.get("style", "normal")

        if weight is not None:
            if not isinstance(weight, int) or not (100 <= weight <= 900):
                raise ValueError(f"weight must be int in range 100-900, got {weight}")

        if style not in ("normal", "italic"):
            raise ValueError(f"style must be 'normal' or 'italic', got {style}")

        registry = get_default_registry()
        font_info = registry.find_font(font_spec, weight=weight, style=style)

        if font_info is None:
            raise ValueError(
                f"gfx:render_text failed to find font '{font_spec}' "
                f"(weight={weight}, style={style})"
            )

        try:
            pil_font = font_info.load(size=size)
        except Exception as e:
            raise ValueError(
                f"gfx:render_text failed to load font '{font_spec}': {e}"
            ) from e

    elif isinstance(font_spec, BlobArtifact):
        # BlobArtifact font - load directly
        # weight and style are ignored for BlobArtifact fonts
        try:
            pil_font = ImageFont.truetype(BytesIO(font_spec.data), size=size)
        except Exception as e:
            raise ValueError(
                f"gfx:render_text failed to load font from BlobArtifact: {e}"
            ) from e

    else:
        raise ValueError(
            f"font must be a string or BlobArtifact, got {type(font_spec)}"
        )

    # Get text bounding box
    # Use a temporary image to measure text
    temp_image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_image)
    bbox = temp_draw.textbbox((0, 0), text, font=pil_font)

    # Calculate tight bounding box
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Create image with tight bounding box
    # Add small padding to avoid clipping
    padding = 2
    image_width = text_width + padding * 2
    image_height = text_height + padding * 2

    image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw text (offset by padding and bbox offset)
    text_x = padding - bbox[0]
    text_y = padding - bbox[1]
    draw.text((text_x, text_y), text, font=pil_font, fill=(r, g, b, a))

    return ImageArtifact(image)
