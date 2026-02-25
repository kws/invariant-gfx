"""Unit tests for gfx:grayscale operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.grayscale import grayscale


class TestGrayscale:
    """Tests for grayscale operation."""

    def test_colored_image_becomes_grayscale(self):
        """Test colored image becomes grayscale."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 128, 0, 255)))

        result = grayscale(image=source)

        assert isinstance(result, ImageArtifact)
        assert result.width == 10 and result.height == 10
        pixel = result.image.getpixel((5, 5))
        assert pixel[0] == pixel[1] == pixel[2]
        assert pixel[3] == 255

    def test_alpha_preserved(self):
        """Test alpha channel is preserved."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (100, 100, 100, 128)))

        result = grayscale(image=source)

        assert result.image.getpixel((0, 0))[3] == 128

    def test_invalid_image_type(self):
        """Test that non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            grayscale(image="not an image")  # type: ignore
