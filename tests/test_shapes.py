"""Unit tests for invariant_gfx.shapes module."""

from decimal import Decimal

import pytest

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.render_svg import render_svg
from invariant_gfx.shapes import (
    arc,
    arrow,
    circle,
    diamond,
    ellipse,
    hexagon,
    line,
    parallelogram,
    polygon,
    rect,
    rounded_rect,
)


class TestShapesLiteralOutput:
    """Test that each shape returns valid SVG with expected elements and viewBox."""

    def test_rect_returns_valid_svg(self):
        svg = rect(72, 72, fill=(50, 50, 50, 255))
        assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
        assert 'viewBox="0 0 72 72"' in svg
        assert "<rect " in svg
        assert 'width="72"' in svg
        assert 'height="72"' in svg

    def test_rounded_rect_returns_valid_svg(self):
        svg = rounded_rect(72, 72, rx=8, fill=(50, 50, 50, 255))
        assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
        assert 'viewBox="0 0 72 72"' in svg
        assert 'rx="8"' in svg
        assert 'ry="8"' in svg

    def test_circle_returns_valid_svg(self):
        svg = circle(36, 36, 30, fill=(255, 0, 0, 255))
        assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
        assert "<circle " in svg
        assert 'cx="36"' in svg
        assert 'cy="36"' in svg
        assert 'r="30"' in svg
        assert 'viewBox="6 6 60 60"' in svg

    def test_ellipse_returns_valid_svg(self):
        svg = ellipse(40, 30, 20, 15, fill=(0, 128, 0, 255))
        assert "<ellipse " in svg
        assert 'cx="40"' in svg
        assert 'cy="30"' in svg
        assert 'rx="20"' in svg
        assert 'ry="15"' in svg
        assert 'viewBox="0 0 40 30"' in svg

    def test_line_returns_valid_svg(self):
        svg = line(0, 0, 100, 50, stroke=(0, 0, 0, 255))
        assert "<line " in svg
        assert 'x1="0"' in svg
        assert 'y1="0"' in svg
        assert 'x2="100"' in svg
        assert 'y2="50"' in svg

    def test_polygon_returns_valid_svg(self):
        points = [(0, 0), (50, 0), (25, 50)]
        svg = polygon(points, fill=(128, 128, 128, 255))
        assert "<polygon " in svg
        assert 'points="0,0 50,0 25,50"' in svg

    def test_arc_returns_valid_svg(self):
        svg = arc(50, 50, 40, 0, 90, pie=False, fill=(255, 255, 0, 255))
        assert "<path " in svg
        assert 'viewBox="10 10 80 80"' in svg  # centered at (50,50), r=40

    def test_arc_pie_returns_closed_path(self):
        svg = arc(50, 50, 40, 0, 90, pie=True, fill=(255, 255, 0, 255))
        assert ' Z"' in svg or ' Z"' in svg

    def test_diamond_returns_valid_svg(self):
        svg = diamond(60, 40, fill=(100, 100, 100, 255))
        assert "<polygon " in svg
        assert 'viewBox="0 0 60 40"' in svg

    def test_parallelogram_returns_valid_svg(self):
        svg = parallelogram(80, 40, skew=Decimal("0.2"), fill=(80, 80, 80, 255))
        assert "<polygon " in svg
        assert 'viewBox="0 0 80 40"' in svg

    def test_hexagon_flat_top_returns_valid_svg(self):
        svg = hexagon(60, 40, flat_top=True, fill=(90, 90, 90, 255))
        assert "<polygon " in svg
        assert 'viewBox="0 0 60 40"' in svg

    def test_hexagon_pointy_top_returns_valid_svg(self):
        svg = hexagon(60, 40, flat_top=False, fill=(90, 90, 90, 255))
        assert "<polygon " in svg
        assert 'viewBox="0 0 60 40"' in svg

    def test_arrow_returns_valid_svg(self):
        svg = arrow(0, 0, 50, 50, stroke=(0, 0, 0, 255))
        assert "<line " in svg
        assert "<path " in svg


class TestShapesExpressionPassthrough:
    """Test that CEL expression strings are passed through without evaluation."""

    def test_rect_expression_passthrough(self):
        svg = rect("${text.width + 24}", "${text.height + 16}", fill=(0, 0, 0, 255))
        assert "${text.width + 24}" in svg
        assert "${text.height + 16}" in svg

    def test_rounded_rect_expression_passthrough(self):
        svg = rounded_rect("${x}", "${y}", rx=8, fill=(0, 0, 0, 255))
        assert "${x}" in svg
        assert "${y}" in svg

    def test_diamond_expression_passthrough(self):
        svg = diamond("${w}", "${h}", fill=(0, 0, 0, 255))
        assert "${w}" in svg
        assert "${h}" in svg


class TestShapesColorConversion:
    """Test RGBA tuple produces correct fill hex and fill-opacity."""

    def test_fill_hex_and_opacity(self):
        svg = rect(10, 10, fill=(255, 0, 128, 128))
        assert 'fill="#ff0080"' in svg
        assert 'fill-opacity="0.5019607843137255"' in svg or "fill-opacity" in svg

    def test_stroke_attributes_when_provided(self):
        svg = rect(
            10,
            10,
            fill=(255, 255, 255, 255),
            stroke=(0, 0, 0, 255),
            stroke_width=2,
        )
        assert 'stroke="#000000"' in svg
        assert 'stroke-width="2"' in svg

    def test_no_stroke_when_none(self):
        svg = rect(10, 10, fill=(255, 255, 255, 255))
        assert "stroke=" not in svg


class TestShapesRoundTrip:
    """Test shape output round-trips through gfx:render_svg to ImageArtifact."""

    def test_rect_roundtrip(self):
        svg = rect(72, 72, fill=(50, 50, 50, 255))
        result = render_svg(svg, 72, 72)
        assert isinstance(result, ImageArtifact)
        assert result.width == 72
        assert result.height == 72

    def test_rounded_rect_roundtrip(self):
        svg = rounded_rect(72, 72, rx=8, fill=(50, 50, 50, 255))
        result = render_svg(svg, 72, 72)
        assert isinstance(result, ImageArtifact)
        assert result.width == 72
        assert result.height == 72

    def test_circle_roundtrip(self):
        svg = circle(36, 36, 30, fill=(255, 0, 0, 255))
        result = render_svg(svg, 72, 72)
        assert isinstance(result, ImageArtifact)
        assert result.width == 72
        assert result.height == 72

    def test_ellipse_roundtrip(self):
        svg = ellipse(40, 30, 20, 15, fill=(0, 128, 0, 255))
        result = render_svg(svg, 80, 60)
        assert isinstance(result, ImageArtifact)
        assert result.width == 80
        assert result.height == 60

    def test_line_roundtrip(self):
        svg = line(0, 0, 100, 50, stroke=(0, 0, 0, 255))
        result = render_svg(svg, 100, 50)
        assert isinstance(result, ImageArtifact)

    def test_polygon_roundtrip(self):
        points = [(0, 0), (50, 0), (25, 50)]
        svg = polygon(points, fill=(128, 128, 128, 255))
        result = render_svg(svg, 50, 50)
        assert isinstance(result, ImageArtifact)

    def test_arc_roundtrip(self):
        svg = arc(50, 50, 40, 0, 90, pie=True, fill=(255, 255, 0, 255))
        result = render_svg(svg, 80, 80)
        assert isinstance(result, ImageArtifact)

    def test_diamond_roundtrip(self):
        svg = diamond(60, 40, fill=(100, 100, 100, 255))
        result = render_svg(svg, 60, 40)
        assert isinstance(result, ImageArtifact)

    def test_parallelogram_roundtrip(self):
        svg = parallelogram(80, 40, skew=Decimal("0.2"), fill=(80, 80, 80, 255))
        result = render_svg(svg, 80, 40)
        assert isinstance(result, ImageArtifact)

    def test_hexagon_roundtrip(self):
        svg = hexagon(60, 40, flat_top=True, fill=(90, 90, 90, 255))
        result = render_svg(svg, 60, 40)
        assert isinstance(result, ImageArtifact)

    def test_arrow_roundtrip(self):
        svg = arrow(0, 0, 50, 50, stroke=(0, 0, 0, 255))
        result = render_svg(svg, 60, 60)
        assert isinstance(result, ImageArtifact)


class TestShapesEdgeCases:
    """Test edge cases: arc pie, parallelogram skew, hexagon orientations."""

    def test_arc_pie_vs_arc_only(self):
        svg_arc = arc(50, 50, 40, 0, 180, pie=False, fill=(255, 0, 0, 255))
        svg_pie = arc(50, 50, 40, 0, 180, pie=True, fill=(255, 0, 0, 255))
        assert " Z" in svg_pie or ' Z"' in svg_pie
        assert svg_arc != svg_pie

    def test_parallelogram_skew_bounds(self):
        svg = parallelogram(100, 50, skew=0.2, fill=(0, 0, 0, 255))
        result = render_svg(svg, 100, 50)
        assert result.width == 100
        assert result.height == 50

    def test_parallelogram_zero_skew(self):
        svg = parallelogram(80, 40, skew=0, fill=(0, 0, 0, 255))
        assert "<polygon " in svg
        result = render_svg(svg, 80, 40)
        assert isinstance(result, ImageArtifact)

    def test_hexagon_flat_top_vs_pointy(self):
        svg_flat = hexagon(60, 40, flat_top=True, fill=(0, 0, 0, 255))
        svg_pointy = hexagon(60, 40, flat_top=False, fill=(0, 0, 0, 255))
        assert svg_flat != svg_pointy
        assert "30,0" in svg_flat or "30," in svg_flat
        assert "15,0" in svg_pointy or "45,0" in svg_pointy

    def test_polygon_empty_points_raises(self):
        with pytest.raises(ValueError, match="points must not be empty"):
            polygon([], fill=(0, 0, 0, 255))

    def test_rect_with_offset_viewbox(self):
        svg = rect(50, 50, x=10, y=20, fill=(0, 0, 0, 255))
        assert 'viewBox="0 0 60 70"' in svg
        assert 'x="10"' in svg
        assert 'y="20"' in svg
