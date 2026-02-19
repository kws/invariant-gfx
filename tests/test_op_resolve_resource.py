"""Unit tests for gfx:resolve_resource operation."""

import pytest

from invariant_gfx.artifacts import BlobArtifact
from invariant_gfx.ops.resolve_resource import resolve_resource


class TestResolveResource:
    """Tests for resolve_resource operation."""

    def test_resolve_lucide_icon(self):
        """Test resolving a Lucide icon."""
        manifest = {
            "name": "lucide:thermometer",
        }

        result = resolve_resource(manifest)

        assert isinstance(result, BlobArtifact)
        assert result.content_type == "image/svg+xml"
        assert len(result.data) > 0

    def test_resolve_material_icon(self):
        """Test resolving a Material Icons icon."""
        manifest = {
            "name": "material-icons:cloud",
        }

        result = resolve_resource(manifest)

        assert isinstance(result, BlobArtifact)
        assert result.content_type == "image/svg+xml"
        assert len(result.data) > 0

    def test_missing_name(self):
        """Test that missing name raises KeyError."""
        manifest = {}

        with pytest.raises(KeyError, match="name"):
            resolve_resource(manifest)

    def test_invalid_name_type(self):
        """Test that non-string name raises ValueError."""
        manifest = {
            "name": 123,
        }

        with pytest.raises(ValueError, match="name must be a string"):
            resolve_resource(manifest)

    def test_nonexistent_resource(self):
        """Test that nonexistent resource raises ValueError."""
        manifest = {
            "name": "nonexistent:resource",
        }

        with pytest.raises(ValueError, match="failed to find resource"):
            resolve_resource(manifest)
