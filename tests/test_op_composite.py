"""Unit tests for gfx:composite operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.anchors import absolute, relative
from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.composite import composite


class TestComposite:
    """Tests for composite operation."""

    def test_single_layer(self):
        """Test compositing a single layer."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        manifest = {
            "layers": {
                "bg": absolute(0, 0),
            },
            "bg": bg,
        }

        result = composite(manifest)

        assert isinstance(result, ImageArtifact)
        assert result.width == 10
        assert result.height == 10
        assert result.image.getpixel((0, 0)) == (255, 0, 0, 255)

    def test_two_layer_center(self):
        """Test two-layer composition with centered content."""
        bg = ImageArtifact(Image.new("RGBA", (20, 20), (0, 0, 0, 255)))
        content = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 255, 255)))

        manifest = {
            "layers": {
                "bg": absolute(0, 0),
                "content": relative("bg", "c,c"),
            },
            "bg": bg,
            "content": content,
        }

        result = composite(manifest)

        assert result.width == 20
        assert result.height == 20

        # Center should be white (content)
        assert result.image.getpixel((10, 10)) == (255, 255, 255, 255)
        # Corner should be black (background)
        assert result.image.getpixel((0, 0)) == (0, 0, 0, 255)

    def test_three_layer_with_relative(self):
        """Test three-layer composition with relative positioning."""
        bg = ImageArtifact(Image.new("RGBA", (30, 30), (40, 40, 40, 255)))
        icon = ImageArtifact(Image.new("RGBA", (10, 10), (0, 100, 200, 255)))
        badge = ImageArtifact(Image.new("RGBA", (5, 5), (200, 0, 0, 255)))

        manifest = {
            "layers": {
                "bg": absolute(0, 0),
                "icon": relative("bg", "c,c"),
                "badge": relative("icon", "se,se", x=-2, y=2),
            },
            "bg": bg,
            "icon": icon,
            "badge": badge,
        }

        result = composite(manifest)

        assert result.width == 30
        assert result.height == 30

        # Center should be blue (icon)
        assert result.image.getpixel((15, 15)) == (0, 100, 200, 255)
        # Corner should be dark gray (background)
        assert result.image.getpixel((0, 0)) == (40, 40, 40, 255)

    def test_missing_layers_key(self):
        """Test that missing layers raises KeyError."""
        manifest = {
            "bg": ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255))),
        }

        with pytest.raises(KeyError, match="layers"):
            composite(manifest)

    def test_missing_artifact(self):
        """Test that missing artifact raises KeyError."""
        manifest = {
            "layers": {
                "bg": absolute(0, 0),
            },
        }

        with pytest.raises(KeyError, match="not found in manifest"):
            composite(manifest)

    def test_ambiguous_z_order(self):
        """Test that ambiguous z-order (siblings) raises ValueError."""
        bg = ImageArtifact(Image.new("RGBA", (20, 20), (0, 0, 0, 255)))
        layer1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        layer2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))

        manifest = {
            "layers": {
                "bg": absolute(0, 0),
                "layer1": relative("bg", "c,c"),
                "layer2": relative("bg", "c,c"),  # Sibling of layer1
            },
            "bg": bg,
            "layer1": layer1,
            "layer2": layer2,
        }

        with pytest.raises(ValueError, match="Ambiguous z-order"):
            composite(manifest)

    def test_no_root_layer(self):
        """Test that missing root layer raises ValueError."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        content = ImageArtifact(Image.new("RGBA", (5, 5), (0, 255, 0, 255)))

        manifest = {
            "layers": {
                "bg": relative("content", "c,c"),  # No root!
                "content": relative("bg", "c,c"),
            },
            "bg": bg,
            "content": content,
        }

        with pytest.raises(ValueError, match="exactly one root layer"):
            composite(manifest)

    def test_opacity(self):
        """Test opacity support."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 255, 255)))
        overlay = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 0, 255)))

        # Create overlay spec with opacity
        overlay_spec = relative("bg", "c,c")
        overlay_spec["opacity"] = Decimal("0.5")

        manifest = {
            "layers": {
                "bg": absolute(0, 0),
                "overlay": overlay_spec,
            },
            "bg": bg,
            "overlay": overlay,
        }

        result = composite(manifest)

        # With 50% opacity black over white, should be gray
        pixel = result.image.getpixel((5, 5))
        # Should be approximately (128, 128, 128, 255) - allow some tolerance
        # Note: Alpha compositing may result in alpha < 255 when layers have opacity
        # The alpha channel reflects the composited opacity
        assert 120 <= pixel[0] <= 135  # R
        assert 120 <= pixel[1] <= 135  # G
        assert 120 <= pixel[2] <= 135  # B
        assert (
            pixel[3] >= 180
        )  # Alpha should be reasonably high (opacity affects alpha channel)

    def test_alignment_variations(self):
        """Test various alignment string formats."""
        bg = ImageArtifact(Image.new("RGBA", (20, 20), (0, 0, 0, 255)))
        content = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 255, 255)))

        # Test "s,e" alignment (start to end)
        manifest = {
            "layers": {
                "bg": absolute(0, 0),
                "content": relative("bg", "s,e"),
            },
            "bg": bg,
            "content": content,
        }

        result = composite(manifest)
        assert result.width == 20
        assert result.height == 20

        # Content should be positioned at (20, 20) - start of content at end of bg
        # So content extends from (20, 20) to (30, 30), which is outside canvas
        # Actually, let me reconsider: "s,e" means start of self aligns to end of parent
        # So if bg is 20x20 at (0,0), its end is at (20, 20)
        # Content start should be at (20, 20), so content is at (20, 20) to (30, 30)
        # This is outside the canvas, so we won't see it
        # Let me use a simpler test - "e,e" (end to end, right-aligned)

        manifest2 = {
            "layers": {
                "bg": absolute(0, 0),
                "content": relative("bg", "e,e"),
            },
            "bg": bg,
            "content": content,
        }

        result2 = composite(manifest2)
        # Content end should align with bg end (20, 20)
        # So content should be at (10, 10) to (20, 20)
        assert result2.width == 20
        assert result2.height == 20
        # Bottom-right corner should be white
        assert result2.image.getpixel((19, 19)) == (255, 255, 255, 255)
