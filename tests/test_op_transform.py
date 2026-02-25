"""Unit tests for gfx:transform operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.transform import transform


class TestTransform:
    """Tests for transform operation."""

    def test_transform_quad_identity(self):
        """Quad with rectangle corners = identity (no transform)."""
        source = ImageArtifact(Image.new("RGBA", (20, 10), (255, 0, 0, 255)))
        # Corners: upper-left, lower-left, lower-right, upper-right
        data = (0, 0, 0, 10, 20, 10, 20, 0)

        result = transform(image=source, method="quad", data=data, size=(20, 10))

        assert isinstance(result, ImageArtifact)
        assert result.width == 20
        assert result.height == 10
        assert result.image.mode == "RGBA"

    def test_transform_quad_perspective(self):
        """Quad with trapezoid (bottom narrower) produces perspective effect."""
        source = ImageArtifact(Image.new("RGBA", (20, 10), (0, 255, 0, 255)))
        # Bottom corners shifted inward by 2px each
        data = (0, 0, 2, 10, 18, 10, 20, 0)

        result = transform(image=source, method="quad", data=data, size=(20, 10))

        assert isinstance(result, ImageArtifact)
        assert result.width == 20
        assert result.height == 10
        assert result.image.mode == "RGBA"

    def test_transform_extent(self):
        """Extent extracts a subregion."""
        source = ImageArtifact(Image.new("RGBA", (30, 20), (0, 0, 255, 255)))
        data = (5, 5, 25, 15)  # x0, y0, x1, y1

        result = transform(image=source, method="extent", data=data, size=(20, 10))

        assert isinstance(result, ImageArtifact)
        assert result.width == 20
        assert result.height == 10

    def test_transform_affine(self):
        """Affine with identity matrix."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (128, 128, 128, 255)))
        # Identity: (1, 0, 0, 0, 1, 0)
        data = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        result = transform(image=source, method="affine", data=data, size=(10, 10))

        assert isinstance(result, ImageArtifact)
        assert result.width == 10
        assert result.height == 10

    def test_transform_with_decimal_data(self):
        """Transform accepts Decimal in data."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (100, 100, 100, 255)))
        data = (0, 0, Decimal("1"), 10, Decimal("9"), 10, 10, 0)

        result = transform(image=source, method="quad", data=data, size=(10, 10))

        assert isinstance(result, ImageArtifact)

    def test_transform_invalid_method(self):
        """Invalid method raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="method must be one of"):
            transform(
                image=source, method="invalid", data=(0, 0, 10, 10), size=(10, 10)
            )

    def test_transform_wrong_data_length(self):
        """Wrong data length raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="must have 8 values"):
            transform(image=source, method="quad", data=(0, 0, 10, 10), size=(10, 10))

    def test_invalid_image_type(self):
        """Non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            transform(
                image="not an image",  # type: ignore
                method="quad",
                data=(0, 0, 0, 10, 10, 10, 10, 0),
                size=(10, 10),
            )
