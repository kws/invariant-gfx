"""Unit tests for gfx:crop_to_content operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.crop_to_content import crop_to_content


class TestCropToContent:
    """Tests for crop_to_content operation."""

    def test_content_with_padding(self):
        """Test trimming transparent padding around content."""
        source = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
        for x in range(5, 15):
            for y in range(5, 15):
                source.putpixel((x, y), (255, 0, 0, 255))
        source = ImageArtifact(source)

        result = crop_to_content(image=source)

        assert result.width == 10
        assert result.height == 10
        assert result.image.getpixel((0, 0)) == (255, 0, 0, 255)

    def test_fully_opaque(self):
        """Test fully opaque image returns same dimensions."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))

        result = crop_to_content(image=source)

        assert result.width == 10
        assert result.height == 20

    def test_fully_transparent(self):
        """Test fully transparent image returns 1x1 transparent pixel."""
        source = ImageArtifact(Image.new("RGBA", (20, 20), (0, 0, 0, 0)))

        result = crop_to_content(image=source)

        assert result.width == 1
        assert result.height == 1
        assert result.image.getpixel((0, 0)) == (0, 0, 0, 0)

    def test_single_pixel_content(self):
        """Test single pixel of content in center."""
        source = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        source.putpixel((5, 5), (255, 255, 255, 255))
        source = ImageArtifact(source)

        result = crop_to_content(image=source)

        assert result.width == 1
        assert result.height == 1
        assert result.image.getpixel((0, 0)) == (255, 255, 255, 255)

    def test_invalid_image_type(self):
        """Test that non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            crop_to_content(image="not an image")  # type: ignore
