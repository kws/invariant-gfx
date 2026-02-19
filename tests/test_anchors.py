"""Unit tests for anchor functions."""

from decimal import Decimal


from invariant_gfx.anchors import absolute, relative


class TestAbsolute:
    """Tests for absolute() anchor function."""

    def test_basic(self):
        """Test basic absolute positioning."""
        spec = absolute(0, 0)

        assert spec["type"] == "absolute"
        assert spec["x"] == 0
        assert spec["y"] == 0

    def test_with_ints(self):
        """Test with integer coordinates."""
        spec = absolute(10, 20)

        assert spec["type"] == "absolute"
        assert spec["x"] == 10
        assert spec["y"] == 20

    def test_with_decimal(self):
        """Test with Decimal coordinates."""
        spec = absolute(Decimal("10.5"), Decimal("20.3"))

        assert spec["type"] == "absolute"
        assert spec["x"] == Decimal("10.5")
        assert spec["y"] == Decimal("20.3")

    def test_with_strings(self):
        """Test with string coordinates (for CEL expressions)."""
        spec = absolute("${width}", "${height}")

        assert spec["type"] == "absolute"
        assert spec["x"] == "${width}"
        assert spec["y"] == "${height}"


class TestRelative:
    """Tests for relative() anchor function."""

    def test_basic(self):
        """Test basic relative positioning."""
        spec = relative("parent", "c,c")

        assert spec["type"] == "relative"
        assert spec["parent"] == "parent"
        assert spec["align"] == "c,c"
        assert spec["x"] == 0
        assert spec["y"] == 0

    def test_with_offsets(self):
        """Test with offset values."""
        spec = relative("parent", "se,se", x=5, y=-5)

        assert spec["type"] == "relative"
        assert spec["parent"] == "parent"
        assert spec["align"] == "se,se"
        assert spec["x"] == 5
        assert spec["y"] == -5

    def test_with_decimal_offsets(self):
        """Test with Decimal offset values."""
        spec = relative("parent", "c,c", x=Decimal("10.5"), y=Decimal("20.3"))

        assert spec["type"] == "relative"
        assert spec["x"] == Decimal("10.5")
        assert spec["y"] == Decimal("20.3")

    def test_with_string_offsets(self):
        """Test with string offsets (for CEL expressions)."""
        spec = relative("parent", "c,c", x="${offset_x}", y="${offset_y}")

        assert spec["type"] == "relative"
        assert spec["x"] == "${offset_x}"
        assert spec["y"] == "${offset_y}"

    def test_various_alignments(self):
        """Test various alignment string formats."""
        # Center-center
        spec1 = relative("parent", "c,c")
        assert spec1["align"] == "c,c"

        # Start-end
        spec2 = relative("parent", "s,e")
        assert spec2["align"] == "s,e"

        # Two-axis alignment
        spec3 = relative("parent", "se,ee")
        assert spec3["align"] == "se,ee"
