"""Unit tests for gfx:rotate operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.rotate import rotate


class TestRotate:
    """Tests for rotate operation."""

    def test_rotate_90_degrees(self):
        """Test 90 degree rotation."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))

        result = rotate(image=source, angle=90)

        assert isinstance(result, ImageArtifact)
        assert result.width == 20
        assert result.height == 10
        assert result.image.mode == "RGBA"

    def test_rotate_180_degrees(self):
        """Test 180 degree rotation."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))

        result = rotate(image=source, angle=180)

        assert result.width == 10
        assert result.height == 20

    def test_rotate_45_degrees_expand(self):
        """Test 45 degree rotation with expand=True (default)."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        result = rotate(image=source, angle=45)

        assert isinstance(result, ImageArtifact)
        assert result.width > 10
        assert result.height > 10
        assert result.image.mode == "RGBA"

    def test_rotate_45_degrees_no_expand(self):
        """Test 45 degree rotation with expand=False."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        result = rotate(image=source, angle=45, expand=False)

        assert result.width == 10
        assert result.height == 10

    def test_rotate_with_decimal(self):
        """Test rotation with Decimal angle."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))

        result = rotate(image=source, angle=Decimal("90"))

        assert result.width == 10
        assert result.height == 10

    def test_rotate_with_string_angle(self):
        """Test rotation with string angle (from CEL expressions)."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 255, 255)))

        result = rotate(image=source, angle="180")

        assert result.width == 10
        assert result.height == 10

    def test_invalid_image_type(self):
        """Test that non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            rotate(image="not an image", angle=90)  # type: ignore
