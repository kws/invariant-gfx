"""Unit tests for gfx:brightness_contrast operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.brightness_contrast import brightness_contrast


class TestBrightnessContrast:
    """Tests for brightness_contrast operation."""

    def test_identity(self):
        """Test brightness=1, contrast=1 returns unchanged image."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (128, 128, 128, 255)))

        result = brightness_contrast(
            image=source,
            brightness=1,
            contrast=1,
        )

        assert isinstance(result, ImageArtifact)
        assert result.width == 10 and result.height == 10
        assert result.image.getpixel((0, 0)) == (128, 128, 128, 255)

    def test_brighten(self):
        """Test brightness > 1 lightens the image."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (100, 100, 100, 255)))

        result = brightness_contrast(image=source, brightness=2)

        pixel = result.image.getpixel((0, 0))
        assert pixel[0] > 100
        assert pixel[3] == 255

    def test_darken(self):
        """Test brightness < 1 darkens the image."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (200, 200, 200, 255)))

        result = brightness_contrast(image=source, brightness=Decimal("0.5"))

        pixel = result.image.getpixel((0, 0))
        assert pixel[0] < 200

    def test_contrast_up(self):
        """Test contrast > 1 increases contrast."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (128, 128, 128, 255)))

        result = brightness_contrast(image=source, contrast=2)

        assert isinstance(result, ImageArtifact)

    def test_contrast_down(self):
        """Test contrast < 1 decreases contrast."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (50, 200, 100, 255)))

        result = brightness_contrast(image=source, contrast=Decimal("0.5"))

        assert isinstance(result, ImageArtifact)

    def test_invalid_image_type(self):
        """Test that non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            brightness_contrast(image="not an image", brightness=1)  # type: ignore
