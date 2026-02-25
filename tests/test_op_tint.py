"""Unit tests for gfx:tint operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.colorize import colorize
from invariant_gfx.ops.extract_alpha import extract_alpha
from invariant_gfx.ops.tint import tint


class TestTint:
    """Tests for tint operation."""

    def test_white_tint_no_change(self):
        """Test white tint (255,255,255) returns unchanged RGB."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (100, 150, 200, 255)))

        result = tint(image=source, color=(255, 255, 255, 255))

        assert result.image.getpixel((0, 0)) == (100, 150, 200, 255)

    def test_red_tint_zeros_gb(self):
        """Test red tint zeros G and B channels."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 255, 255)))

        result = tint(image=source, color=(255, 0, 0, 255))

        pixel = result.image.getpixel((0, 0))
        assert pixel[0] == 255
        assert pixel[1] == 0
        assert pixel[2] == 0
        assert pixel[3] == 255

    def test_alpha_preserved(self):
        """Test source alpha is preserved."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 255, 128)))

        result = tint(image=source, color=(128, 128, 128, 255))

        assert result.image.getpixel((0, 0))[3] == 128

    def test_tint_vs_colorize(self):
        """Test tint preserves structure; colorize produces flat fill."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (200, 100, 50, 255)))

        tinted = tint(image=source, color=(0, 0, 255, 255))
        alpha_mask = extract_alpha(source)
        colorized = colorize(image=alpha_mask, color=(0, 0, 255, 255))

        tinted_pixel = tinted.image.getpixel((0, 0))
        colorized_pixel = colorized.image.getpixel((0, 0))

        assert tinted_pixel[0] < 255
        assert tinted_pixel[2] > 0
        assert colorized_pixel == (0, 0, 255, 255)

    def test_invalid_image_type(self):
        """Test that non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            tint(image="not an image", color=(255, 0, 0, 255))  # type: ignore

    def test_invalid_color(self):
        """Test invalid color raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        with pytest.raises(ValueError, match="0-255"):
            tint(image=source, color=(255, 0, 0, 256))  # type: ignore
