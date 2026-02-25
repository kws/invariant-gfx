"""Unit tests for gfx:gradient_opacity operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.gradient_opacity import gradient_opacity


class TestGradientOpacity:
    """Tests for gradient_opacity operation."""

    def test_angle_90_top_to_bottom(self):
        """Angle 90: top opaque, bottom transparent."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        result = gradient_opacity(
            image=source,
            angle=90,
            start=Decimal("1"),
            end=Decimal("0"),
        )
        # Top row should be opaque, bottom row transparent
        assert result.image.getpixel((5, 0))[3] > 200
        assert result.image.getpixel((5, 9))[3] < 50

    def test_angle_0_left_to_right(self):
        """Angle 0: left opaque, right transparent."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))
        result = gradient_opacity(
            image=source,
            angle=0,
            start=1,
            end=0,
        )
        assert result.image.getpixel((0, 5))[3] > 200
        assert result.image.getpixel((9, 5))[3] < 50

    def test_angle_180_right_to_left(self):
        """Angle 180: right opaque, left transparent."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 255, 255)))
        result = gradient_opacity(
            image=source,
            angle=180,
            start=1,
            end=0,
        )
        assert result.image.getpixel((9, 5))[3] > 200
        assert result.image.getpixel((0, 5))[3] < 50

    def test_start_end_reversed(self):
        """Start 0, end 1: gradient inverted."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 0, 255)))
        result = gradient_opacity(
            image=source,
            angle=90,
            start=0,
            end=1,
        )
        # Top transparent, bottom opaque
        assert result.image.getpixel((5, 0))[3] < 50
        assert result.image.getpixel((5, 9))[3] > 200

    def test_rgb_unchanged(self):
        """RGB channels are preserved."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (100, 150, 200, 255)))
        result = gradient_opacity(
            image=source, angle=90, start=Decimal("0.5"), end=Decimal("0.5")
        )
        assert result.image.getpixel((4, 4))[:3] == (100, 150, 200)

    def test_dimensions_unchanged(self):
        """Output size equals input size."""
        source = ImageArtifact(Image.new("RGBA", (24, 16), (0, 0, 0, 255)))
        result = gradient_opacity(image=source, angle=45, start=1, end=0)
        assert result.width == 24 and result.height == 16

    def test_invalid_image_type(self):
        """Non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="image must be ImageArtifact"):
            gradient_opacity(image="not an image", angle=90)  # type: ignore[arg-type]

    def test_invalid_start_negative_raises(self):
        """Start < 0 raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="start must be in range"):
            gradient_opacity(image=source, angle=90, start=Decimal("-0.1"), end=0)

    def test_invalid_end_above_one_raises(self):
        """End > 1 raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="end must be in range"):
            gradient_opacity(image=source, angle=90, start=1, end=Decimal("1.5"))

    def test_decimal_params_accepted(self):
        """Decimal angle, start, end work."""
        source = ImageArtifact(Image.new("RGBA", (6, 6), (0, 0, 0, 255)))
        result = gradient_opacity(
            image=source,
            angle=Decimal("90"),
            start=Decimal("1"),
            end=Decimal("0"),
        )
        assert result.width == 6 and result.height == 6
        assert result.image.getpixel((3, 0))[3] > result.image.getpixel((3, 5))[3]

    def test_start_pos_end_pos_halfway_fade(self):
        """PowerPoint-style: fade completes halfway, bottom half fully transparent."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        result = gradient_opacity(
            image=source,
            angle=90,
            start=1,
            end=0,
            start_pos=Decimal("0"),
            end_pos=Decimal("0.5"),
        )
        # Top (near y=0): opaque
        assert result.image.getpixel((5, 0))[3] > 200
        # Middle (y=4): near transparent (end of gradient)
        assert result.image.getpixel((5, 4))[3] < 80
        # Bottom half (y>=5): fully transparent
        assert result.image.getpixel((5, 5))[3] < 10
        assert result.image.getpixel((5, 9))[3] < 10

    def test_start_pos_end_pos_invalid_order_raises(self):
        """start_pos >= end_pos raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="start_pos must be less than end_pos"):
            gradient_opacity(
                image=source,
                angle=90,
                start_pos=Decimal("0.5"),
                end_pos=Decimal("0.5"),
            )
