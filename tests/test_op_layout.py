"""Unit tests for gfx:layout operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.layout import layout


class TestLayout:
    """Tests for layout operation."""

    def test_row_layout_basic(self):
        """Test basic row layout."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (15, 25), (0, 255, 0, 255)))

        manifest = {
            "direction": "row",
            "align": "c",
            "gap": Decimal("5"),
            "items": ["item1", "item2"],
            "item1": item1,
            "item2": item2,
        }

        result = layout(manifest)

        assert isinstance(result, ImageArtifact)
        # Width = 10 + 5 + 15 = 30
        assert result.width == 30
        # Height = max(20, 25) = 25
        assert result.height == 25

    def test_column_layout_basic(self):
        """Test basic column layout."""
        item1 = ImageArtifact(Image.new("RGBA", (20, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (25, 15), (0, 255, 0, 255)))

        manifest = {
            "direction": "column",
            "align": "c",
            "gap": Decimal("5"),
            "items": ["item1", "item2"],
            "item1": item1,
            "item2": item2,
        }

        result = layout(manifest)

        # Width = max(20, 25) = 25
        assert result.width == 25
        # Height = 10 + 5 + 15 = 30
        assert result.height == 30

    def test_row_align_start(self):
        """Test row layout with start alignment."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))

        manifest = {
            "direction": "row",
            "align": "s",
            "gap": Decimal("0"),
            "items": ["item1", "item2"],
            "item1": item1,
            "item2": item2,
        }

        result = layout(manifest)

        # Both items should be at y=0 (start)
        assert result.height == 20  # max height

    def test_row_align_end(self):
        """Test row layout with end alignment."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 20), (0, 255, 0, 255)))

        manifest = {
            "direction": "row",
            "align": "e",
            "gap": Decimal("0"),
            "items": ["item1", "item2"],
            "item1": item1,
            "item2": item2,
        }

        result = layout(manifest)

        # item1 should be at bottom (y = 20 - 10 = 10)
        assert result.height == 20

    def test_column_align_start(self):
        """Test column layout with start alignment."""
        item1 = ImageArtifact(Image.new("RGBA", (20, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))

        manifest = {
            "direction": "column",
            "align": "s",
            "gap": Decimal("0"),
            "items": ["item1", "item2"],
            "item1": item1,
            "item2": item2,
        }

        result = layout(manifest)

        # Both items should be at x=0 (start)
        assert result.width == 20  # max width

    def test_column_align_end(self):
        """Test column layout with end alignment."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (20, 10), (0, 255, 0, 255)))

        manifest = {
            "direction": "column",
            "align": "e",
            "gap": Decimal("0"),
            "items": ["item1", "item2"],
            "item1": item1,
            "item2": item2,
        }

        result = layout(manifest)

        # item1 should be at right (x = 20 - 10 = 10)
        assert result.width == 20

    def test_with_int_gap(self):
        """Test with integer gap."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))

        manifest = {
            "direction": "row",
            "align": "c",
            "gap": 10,
            "items": ["item1", "item2"],
            "item1": item1,
            "item2": item2,
        }

        result = layout(manifest)

        # Width = 10 + 10 + 10 = 30
        assert result.width == 30

    def test_with_string_gap(self):
        """Test with string gap (from CEL expressions)."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))

        manifest = {
            "direction": "row",
            "align": "c",
            "gap": "15",
            "items": ["item1", "item2"],
            "item1": item1,
            "item2": item2,
        }

        result = layout(manifest)

        # Width = 10 + 15 + 10 = 35
        assert result.width == 35

    def test_zero_gap(self):
        """Test with zero gap."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))

        manifest = {
            "direction": "row",
            "align": "c",
            "gap": Decimal("0"),
            "items": ["item1", "item2"],
            "item1": item1,
            "item2": item2,
        }

        result = layout(manifest)

        # Width = 10 + 0 + 10 = 20
        assert result.width == 20

    def test_three_items(self):
        """Test layout with three items."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))
        item3 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 255, 255)))

        manifest = {
            "direction": "row",
            "align": "c",
            "gap": Decimal("5"),
            "items": ["item1", "item2", "item3"],
            "item1": item1,
            "item2": item2,
            "item3": item3,
        }

        result = layout(manifest)

        # Width = 10 + 5 + 10 + 5 + 10 = 40
        assert result.width == 40

    def test_missing_direction(self):
        """Test that missing direction raises KeyError."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        manifest = {
            "align": "c",
            "gap": Decimal("5"),
            "items": ["item1"],
            "item1": item1,
        }

        with pytest.raises(KeyError, match="direction"):
            layout(manifest)

    def test_missing_align(self):
        """Test that missing align raises KeyError."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        manifest = {
            "direction": "row",
            "gap": Decimal("5"),
            "items": ["item1"],
            "item1": item1,
        }

        with pytest.raises(KeyError, match="align"):
            layout(manifest)

    def test_missing_gap(self):
        """Test that missing gap raises KeyError."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        manifest = {
            "direction": "row",
            "align": "c",
            "items": ["item1"],
            "item1": item1,
        }

        with pytest.raises(KeyError, match="gap"):
            layout(manifest)

    def test_missing_items(self):
        """Test that missing items raises KeyError."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        manifest = {
            "direction": "row",
            "align": "c",
            "gap": Decimal("5"),
            "item1": item1,
        }

        with pytest.raises(KeyError, match="items"):
            layout(manifest)

    def test_invalid_direction(self):
        """Test that invalid direction raises ValueError."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        manifest = {
            "direction": "diagonal",
            "align": "c",
            "gap": Decimal("5"),
            "items": ["item1"],
            "item1": item1,
        }

        with pytest.raises(ValueError, match="direction must be 'row' or 'column'"):
            layout(manifest)

    def test_invalid_align(self):
        """Test that invalid align raises ValueError."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        manifest = {
            "direction": "row",
            "align": "x",
            "gap": Decimal("5"),
            "items": ["item1"],
            "item1": item1,
        }

        with pytest.raises(ValueError, match="align must be 's', 'c', or 'e'"):
            layout(manifest)

    def test_empty_items(self):
        """Test that empty items raises ValueError."""
        manifest = {
            "direction": "row",
            "align": "c",
            "gap": Decimal("5"),
            "items": [],
        }

        with pytest.raises(ValueError, match="items must contain at least one item"):
            layout(manifest)

    def test_missing_item_artifact(self):
        """Test that missing item artifact raises KeyError."""
        manifest = {
            "direction": "row",
            "align": "c",
            "gap": Decimal("5"),
            "items": ["item1"],
        }

        with pytest.raises(KeyError, match="not found in manifest"):
            layout(manifest)

    def test_negative_gap(self):
        """Test that negative gap raises ValueError."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        manifest = {
            "direction": "row",
            "align": "c",
            "gap": Decimal("-5"),
            "items": ["item1"],
            "item1": item1,
        }

        with pytest.raises(ValueError, match="gap must be non-negative"):
            layout(manifest)
