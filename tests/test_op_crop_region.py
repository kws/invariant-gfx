"""Unit tests for gfx:crop_region operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.crop_region import crop_region


class TestCropRegion:
    """Tests for crop_region operation."""

    def test_basic_region(self):
        """Test extracting a basic region."""
        source = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
        for x in range(5, 15):
            for y in range(5, 15):
                source.putpixel((x, y), (255, 0, 0, 255))
        source = ImageArtifact(source)

        result = crop_region(image=source, x=5, y=5, width=10, height=10)

        assert result.width == 10
        assert result.height == 10
        assert result.image.getpixel((0, 0)) == (255, 0, 0, 255)

    def test_full_image(self):
        """Test extracting full image region."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (100, 100, 100, 255)))

        result = crop_region(image=source, x=0, y=0, width=10, height=20)

        assert result.width == 10
        assert result.height == 20

    def test_with_decimal_params(self):
        """Test with Decimal params (CEL compatibility)."""
        source = ImageArtifact(Image.new("RGBA", (20, 20), (255, 0, 0, 255)))

        result = crop_region(
            image=source,
            x=Decimal("5"),
            y=Decimal("5"),
            width=Decimal("10"),
            height=Decimal("10"),
        )

        assert result.width == 10
        assert result.height == 10

    def test_out_of_bounds_raises(self):
        """Test out-of-bounds region raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        with pytest.raises(ValueError, match="exceeds image width"):
            crop_region(image=source, x=5, y=5, width=10, height=10)

    def test_negative_dimensions_raise(self):
        """Test negative width/height raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        with pytest.raises(ValueError, match="must be positive"):
            crop_region(image=source, x=0, y=0, width=-1, height=5)

    def test_invalid_image_type(self):
        """Test that non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            crop_region(
                image="not an image",  # type: ignore
                x=0,
                y=0,
                width=10,
                height=10,
            )
