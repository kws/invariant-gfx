"""Graphics operations package."""

from typing import Any

from invariant_gfx.ops.composite import composite
from invariant_gfx.ops.create_solid import create_solid

# Package of graphics operations
OPS: dict[str, Any] = {
    "create_solid": create_solid,
    "composite": composite,
}
