"""Unit tests for gfx:thumbnail operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.thumbnail import thumbnail


class TestThumbnail:
    """Tests for thumbnail operation."""

    def test_contain_letterbox(self):
        """Test contain mode (letterbox) - fit inside, pad to fill."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))

        result = thumbnail(image=source, width=30, height=30, mode="contain")

        assert result.width == 30
        assert result.height == 30
        assert result.image.mode == "RGBA"
        # 10x20 fits in 30x30: scale = min(3, 1.5) = 1.5 -> 15x30
        # Center in 30x30: paste at (7, 0)
        assert result.image.getpixel((0, 0)) == (0, 0, 0, 0)  # transparent padding
        assert result.image.getpixel((15, 15)) == (255, 0, 0, 255)  # image content

    def test_cover_crop(self):
        """Test cover mode (crop) - scale to fill, crop excess."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))

        result = thumbnail(image=source, width=30, height=30, mode="cover")

        assert result.width == 30
        assert result.height == 30
        # 10x20 covers 30x30: scale = max(3, 1.5) = 3 -> 30x60, crop center 30x30

    def test_contain_square_source_to_rect(self):
        """Test contain with square source to rectangular target."""
        source = ImageArtifact(Image.new("RGBA", (20, 20), (0, 255, 0, 255)))

        result = thumbnail(image=source, width=40, height=20, mode="contain")

        assert result.width == 40
        assert result.height == 20
        # 20x20 fits in 40x20: scale = min(2, 1) = 1 -> 20x20, pad to 40x20

    def test_cover_rect_source_to_square(self):
        """Test cover with rectangular source to square target."""
        source = ImageArtifact(Image.new("RGBA", (20, 10), (0, 0, 255, 255)))

        result = thumbnail(image=source, width=20, height=20, mode="cover")

        assert result.width == 20
        assert result.height == 20
        # 20x10 covers 20x20: scale = max(1, 2) = 2 -> 40x20, crop center 20x20

    def test_invalid_mode_raises(self):
        """Test that invalid mode raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        with pytest.raises(ValueError, match="mode must be"):
            thumbnail(image=source, width=20, height=20, mode="invalid")

    def test_invalid_image_type(self):
        """Test that non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            thumbnail(image="not an image", width=20, height=20)  # type: ignore

    def test_with_decimal_dimensions(self):
        """Test with Decimal dimensions."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        result = thumbnail(
            image=source,
            width=Decimal("20"),
            height=Decimal("20"),
            mode="contain",
        )

        assert result.width == 20
        assert result.height == 20
