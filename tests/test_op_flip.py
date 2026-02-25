"""Unit tests for gfx:flip operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.flip import flip


class TestFlip:
    """Tests for flip operation."""

    def test_flip_horizontal(self):
        """Test horizontal flip."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))

        result = flip(image=source, horizontal=True)

        assert isinstance(result, ImageArtifact)
        assert result.width == 10
        assert result.height == 20
        assert result.image.mode == "RGBA"

    def test_flip_vertical(self):
        """Test vertical flip."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))

        result = flip(image=source, vertical=True)

        assert isinstance(result, ImageArtifact)
        assert result.width == 10
        assert result.height == 20

    def test_flip_both(self):
        """Test flip both horizontal and vertical."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))

        result = flip(image=source, horizontal=True, vertical=True)

        assert isinstance(result, ImageArtifact)
        assert result.width == 10
        assert result.height == 20

    def test_flip_none_returns_same_instance(self):
        """Test that both False returns same artifact (no-op)."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))

        result = flip(image=source, horizontal=False, vertical=False)

        assert result is source

    def test_invalid_image_type(self):
        """Test that non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            flip(image="not an image", horizontal=True)  # type: ignore
