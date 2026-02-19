"""Unit tests for gfx:create_solid operation."""

from decimal import Decimal

import pytest

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.create_solid import create_solid


class TestCreateSolid:
    """Tests for create_solid operation."""

    def test_basic_creation(self):
        """Test basic solid color creation."""
        manifest = {
            "size": (Decimal("10"), Decimal("20")),
            "color": (255, 128, 64, 255),
        }

        result = create_solid(manifest)

        assert isinstance(result, ImageArtifact)
        assert result.width == 10
        assert result.height == 20
        assert result.image.mode == "RGBA"

        # Check pixel color
        pixel = result.image.getpixel((0, 0))
        assert pixel == (255, 128, 64, 255)

    def test_with_int_size(self):
        """Test with integer size values."""
        manifest = {
            "size": (10, 20),
            "color": (0, 0, 0, 255),
        }

        result = create_solid(manifest)

        assert result.width == 10
        assert result.height == 20

    def test_with_string_size(self):
        """Test with string size values (from CEL expressions)."""
        manifest = {
            "size": ("10", "20"),
            "color": (255, 255, 255, 255),
        }

        result = create_solid(manifest)

        assert result.width == 10
        assert result.height == 20

    def test_missing_size(self):
        """Test that missing size raises KeyError."""
        manifest = {
            "color": (255, 0, 0, 255),
        }

        with pytest.raises(KeyError, match="size"):
            create_solid(manifest)

    def test_missing_color(self):
        """Test that missing color raises KeyError."""
        manifest = {
            "size": (10, 10),
        }

        with pytest.raises(KeyError, match="color"):
            create_solid(manifest)

    def test_invalid_size(self):
        """Test that invalid size raises ValueError."""
        manifest = {
            "size": (10,),  # Wrong length
            "color": (255, 0, 0, 255),
        }

        with pytest.raises(ValueError, match="size must be a tuple"):
            create_solid(manifest)

    def test_invalid_color(self):
        """Test that invalid color raises ValueError."""
        manifest = {
            "size": (10, 10),
            "color": (255, 0, 0),  # Missing alpha
        }

        with pytest.raises(ValueError, match="color must be a tuple"):
            create_solid(manifest)

    def test_negative_size(self):
        """Test that negative size raises ValueError."""
        manifest = {
            "size": (-10, 10),
            "color": (255, 0, 0, 255),
        }

        with pytest.raises(ValueError, match="size must be positive"):
            create_solid(manifest)

    def test_invalid_color_range(self):
        """Test that color values out of range raise ValueError."""
        manifest = {
            "size": (10, 10),
            "color": (256, 0, 0, 255),  # Out of range
        }

        with pytest.raises(ValueError, match="color values must be int in range"):
            create_solid(manifest)

    def test_different_colors(self):
        """Test that different colors produce different images."""
        manifest1 = {
            "size": (10, 10),
            "color": (255, 0, 0, 255),  # Red
        }
        manifest2 = {
            "size": (10, 10),
            "color": (0, 255, 0, 255),  # Green
        }

        result1 = create_solid(manifest1)
        result2 = create_solid(manifest2)

        assert result1.image.getpixel((0, 0)) == (255, 0, 0, 255)
        assert result2.image.getpixel((0, 0)) == (0, 255, 0, 255)
        assert result1.get_stable_hash() != result2.get_stable_hash()
