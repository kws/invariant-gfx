"""Graphics operations package."""

from typing import Any

from invariant_gfx.ops.blob_to_image import blob_to_image
from invariant_gfx.ops.composite import composite
from invariant_gfx.ops.create_solid import create_solid
from invariant_gfx.ops.layout import layout
from invariant_gfx.ops.render_svg import render_svg
from invariant_gfx.ops.render_text import render_text
from invariant_gfx.ops.resolve_resource import resolve_resource
from invariant_gfx.ops.resize import resize

# Package of graphics operations
OPS: dict[str, Any] = {
    "create_solid": create_solid,
    "composite": composite,
    "resize": resize,
    "blob_to_image": blob_to_image,
    "layout": layout,
    "resolve_resource": resolve_resource,
    "render_svg": render_svg,
    "render_text": render_text,
}
