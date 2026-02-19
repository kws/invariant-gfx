"""Unit tests for gfx:render_text operation."""

from decimal import Decimal

import pytest

from invariant_gfx.artifacts import BlobArtifact, ImageArtifact
from invariant_gfx.ops.render_text import render_text


class TestRenderText:
    """Tests for render_text operation."""

    def test_basic_text_rendering(self):
        """Test basic text rendering with string font."""
        manifest = {
            "text": "Hello",
            "font": "Geneva",
            "size": Decimal("24"),
            "color": (255, 0, 0, 255),
        }

        result = render_text(manifest)

        assert isinstance(result, ImageArtifact)
        assert result.image.mode == "RGBA"
        # Text should have positive dimensions
        assert result.width > 0
        assert result.height > 0

    def test_with_int_size(self):
        """Test with integer size."""
        manifest = {
            "text": "Test",
            "font": "Geneva",
            "size": 12,
            "color": (0, 255, 0, 255),
        }

        result = render_text(manifest)

        assert result.width > 0
        assert result.height > 0

    def test_with_string_size(self):
        """Test with string size (from CEL expressions)."""
        manifest = {
            "text": "Test",
            "font": "Geneva",
            "size": "18",
            "color": (0, 0, 255, 255),
        }

        result = render_text(manifest)

        assert result.width > 0
        assert result.height > 0

    def test_with_font_weight(self):
        """Test with font weight parameter."""
        manifest = {
            "text": "Bold",
            "font": "Geneva",
            "size": 24,
            "color": (255, 255, 255, 255),
            "weight": 700,
        }

        result = render_text(manifest)

        assert result.width > 0
        assert result.height > 0

    def test_with_font_style(self):
        """Test with font style parameter."""
        manifest = {
            "text": "Italic",
            "font": "Geneva",
            "size": 24,
            "color": (255, 255, 255, 255),
            "style": "normal",
        }

        result = render_text(manifest)

        assert result.width > 0
        assert result.height > 0

    def test_with_blob_font(self):
        """Test with BlobArtifact font."""
        # Load a font file as blob
        # We'll use a system font path
        from pathlib import Path

        # Try to find a system font
        font_paths = [
            "/System/Library/Fonts/Geneva.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]

        font_data = None
        for path in font_paths:
            if Path(path).exists():
                font_data = Path(path).read_bytes()
                break

        if font_data is None:
            pytest.skip("No system font found for testing")

        font_blob = BlobArtifact(data=font_data, content_type="font/ttf")

        manifest = {
            "text": "Blob Font",
            "font": font_blob,
            "size": 24,
            "color": (255, 0, 0, 255),
        }

        result = render_text(manifest)

        assert isinstance(result, ImageArtifact)
        assert result.width > 0
        assert result.height > 0

    def test_missing_text(self):
        """Test that missing text raises KeyError."""
        manifest = {
            "font": "Geneva",
            "size": 24,
            "color": (255, 0, 0, 255),
        }

        with pytest.raises(KeyError, match="text"):
            render_text(manifest)

    def test_missing_font(self):
        """Test that missing font raises KeyError."""
        manifest = {
            "text": "Hello",
            "size": 24,
            "color": (255, 0, 0, 255),
        }

        with pytest.raises(KeyError, match="font"):
            render_text(manifest)

    def test_missing_size(self):
        """Test that missing size raises KeyError."""
        manifest = {
            "text": "Hello",
            "font": "Geneva",
            "color": (255, 0, 0, 255),
        }

        with pytest.raises(KeyError, match="size"):
            render_text(manifest)

    def test_missing_color(self):
        """Test that missing color raises KeyError."""
        manifest = {
            "text": "Hello",
            "font": "Geneva",
            "size": 24,
        }

        with pytest.raises(KeyError, match="color"):
            render_text(manifest)

    def test_invalid_font_type(self):
        """Test that invalid font type raises ValueError."""
        manifest = {
            "text": "Hello",
            "font": 123,  # Invalid type
            "size": 24,
            "color": (255, 0, 0, 255),
        }

        with pytest.raises(ValueError, match="font must be a string or BlobArtifact"):
            render_text(manifest)

    def test_invalid_font_name(self):
        """Test that invalid font name raises ValueError."""
        manifest = {
            "text": "Hello",
            "font": "NonexistentFont12345",
            "size": 24,
            "color": (255, 0, 0, 255),
        }

        with pytest.raises(ValueError, match="failed to find font"):
            render_text(manifest)

    def test_invalid_weight(self):
        """Test that invalid weight raises ValueError."""
        manifest = {
            "text": "Hello",
            "font": "Geneva",
            "size": 24,
            "color": (255, 0, 0, 255),
            "weight": 50,  # Too low
        }

        with pytest.raises(ValueError, match="weight must be int in range"):
            render_text(manifest)

    def test_invalid_style(self):
        """Test that invalid style raises ValueError."""
        manifest = {
            "text": "Hello",
            "font": "Geneva",
            "size": 24,
            "color": (255, 0, 0, 255),
            "style": "bold",  # Invalid
        }

        with pytest.raises(ValueError, match="style must be 'normal' or 'italic'"):
            render_text(manifest)

    def test_negative_size(self):
        """Test that negative size raises ValueError."""
        manifest = {
            "text": "Hello",
            "font": "Geneva",
            "size": -10,
            "color": (255, 0, 0, 255),
        }

        with pytest.raises(ValueError, match="size must be positive"):
            render_text(manifest)

    def test_invalid_color(self):
        """Test that invalid color raises ValueError."""
        manifest = {
            "text": "Hello",
            "font": "Geneva",
            "size": 24,
            "color": (255, 0, 0),  # Missing alpha
        }

        with pytest.raises(ValueError, match="color must be a tuple"):
            render_text(manifest)

    def test_tight_bounding_box(self):
        """Test that output has tight bounding box."""
        manifest = {
            "text": "Hi",
            "font": "Geneva",
            "size": 24,
            "color": (255, 0, 0, 255),
        }

        result = render_text(manifest)

        # Should have reasonable dimensions (not too large)
        assert result.width < 100  # "Hi" should be small
        assert result.height < 50
