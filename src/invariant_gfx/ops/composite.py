"""gfx:composite operation - fixed-size composition engine."""

from decimal import Decimal
from typing import Any

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def composite(manifest: dict[str, Any]) -> ICacheable:
    """Composite multiple layers onto a fixed-size canvas.

    Args:
        manifest: Must contain:
            - 'layers': dict[str, dict] mapping dependency IDs to anchor specs
            - Artifacts for each dependency ID (as ImageArtifact)

    Returns:
        ImageArtifact with composited result.

    Raises:
        KeyError: If required keys are missing.
        ValueError: If z-order is ambiguous or positioning fails.
    """
    if "layers" not in manifest:
        raise KeyError("gfx:composite requires 'layers' in manifest")

    layers = manifest["layers"]
    if not isinstance(layers, dict):
        raise ValueError(f"layers must be a dict, got {type(layers)}")

    # Extract artifacts for each layer
    artifacts: dict[str, ImageArtifact] = {}
    for layer_id in layers.keys():
        if layer_id not in manifest:
            raise KeyError(
                f"Layer '{layer_id}' not found in manifest. "
                f"Make sure it's listed in node.deps."
            )
        artifact = manifest[layer_id]
        if not isinstance(artifact, ImageArtifact):
            raise ValueError(
                f"Layer '{layer_id}' must be ImageArtifact, got {type(artifact)}"
            )
        artifacts[layer_id] = artifact

    # Determine z-order from parent topology
    z_order = _determine_z_order(layers)

    # Find the root layer (first in z-order, must be absolute)
    root_id = z_order[0]
    root_spec = layers[root_id]
    if root_spec.get("type") != "absolute":
        raise ValueError(
            f"First layer in z-order ('{root_id}') must use absolute() positioning"
        )

    # Get root layer dimensions (defines canvas size)
    root_artifact = artifacts[root_id]
    canvas_width = root_artifact.width
    canvas_height = root_artifact.height

    # Create canvas
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))

    # Track placed layers for relative positioning
    placed: dict[
        str, tuple[int, int, int, int]
    ] = {}  # layer_id -> (x, y, width, height)

    # Composite layers in z-order
    for layer_id in z_order:
        layer_spec = layers[layer_id]
        artifact = artifacts[layer_id]

        # Resolve position
        x, y = _resolve_position(
            layer_spec, layer_id, artifacts, placed, canvas_width, canvas_height
        )

        # Get optional properties
        mode = layer_spec.get("mode", "normal")
        opacity_val = layer_spec.get("opacity", 1.0)

        # Convert opacity
        if isinstance(opacity_val, Decimal):
            opacity = float(opacity_val)
        elif isinstance(opacity_val, (int, float, str)):
            opacity = float(opacity_val)
        else:
            opacity = 1.0

        opacity = max(0.0, min(1.0, opacity))  # Clamp to [0, 1]

        # Apply opacity if needed
        layer_image = artifact.image
        if opacity < 1.0:
            # Create a copy with adjusted alpha
            layer_image = layer_image.copy()
            alpha = layer_image.split()[3]
            alpha = alpha.point(lambda p: int(p * opacity))
            layer_image.putalpha(alpha)

        # Composite onto canvas
        # For now, we only support "normal" blend mode
        # Other blend modes (multiply, screen, etc.) require more complex logic
        # and can be added in a future iteration
        if mode != "normal":
            # TODO: Implement other blend modes
            # For now, fall back to normal mode
            pass

        # Paste with alpha channel support
        if layer_image.mode == "RGBA":
            canvas.paste(layer_image, (x, y), layer_image)
        else:
            canvas.paste(layer_image, (x, y))

        # Record placement for relative positioning
        placed[layer_id] = (x, y, artifact.width, artifact.height)

    return ImageArtifact(canvas)


def _determine_z_order(layers: dict[str, dict[str, Any]]) -> list[str]:
    """Determine z-order from parent topology.

    Returns layers in draw order (bottom to top).
    Raises ValueError if z-order is ambiguous (siblings share parent).
    """
    # Build parent map
    parent_map: dict[str, str | None] = {}
    for layer_id, spec in layers.items():
        if spec.get("type") == "relative":
            parent = spec.get("parent")
            if not isinstance(parent, str):
                raise ValueError(
                    f"Layer '{layer_id}' relative() anchor must have 'parent' as string"
                )
            parent_map[layer_id] = parent
        else:
            parent_map[layer_id] = None

    # Find root (no parent)
    roots = [lid for lid, parent in parent_map.items() if parent is None]
    if len(roots) != 1:
        raise ValueError(
            f"Composite must have exactly one root layer (absolute positioning), "
            f"found {len(roots)}: {roots}"
        )

    root = roots[0]

    # Build child map to detect siblings
    children: dict[str, list[str]] = {}
    for layer_id, parent in parent_map.items():
        if parent is not None:
            if parent not in children:
                children[parent] = []
            children[parent].append(layer_id)

    # Check for siblings (ambiguous z-order)
    for parent, siblings in children.items():
        if len(siblings) > 1:
            raise ValueError(
                f"Ambiguous z-order: multiple layers share parent '{parent}': {siblings}. "
                f"Restructure to form a chain or use explicit layer_order (future enhancement)."
            )

    # Build z-order by following the chain
    z_order = [root]
    current = root

    while current in children:
        # Should be exactly one child (we checked for siblings above)
        child = children[current][0]
        z_order.append(child)
        current = child

    # Verify all layers are included
    if len(z_order) != len(layers):
        missing = set(layers.keys()) - set(z_order)
        raise ValueError(
            f"Z-order determination incomplete. Missing layers: {missing}. "
            f"This may indicate a cycle or disconnected layers."
        )

    return z_order


def _resolve_position(
    spec: dict[str, Any],
    layer_id: str,
    artifacts: dict[str, ImageArtifact],
    placed: dict[str, tuple[int, int, int, int]],
    canvas_width: int,
    canvas_height: int,
) -> tuple[int, int]:
    """Resolve layer position from anchor spec.

    Returns:
        (x, y) pixel coordinates.
    """
    anchor_type = spec.get("type")

    if anchor_type == "absolute":
        x = _to_int(spec.get("x", 0))
        y = _to_int(spec.get("y", 0))
        return (x, y)

    elif anchor_type == "relative":
        parent_id = spec.get("parent")
        if not isinstance(parent_id, str):
            raise ValueError(
                f"Layer '{layer_id}' relative() anchor must have 'parent' as string"
            )

        if parent_id not in placed:
            raise ValueError(
                f"Layer '{layer_id}' references parent '{parent_id}' which hasn't been placed yet. "
                f"This indicates a z-order issue."
            )

        align_str = spec.get("align", "c,c")
        x_offset = _to_int(spec.get("x", 0))
        y_offset = _to_int(spec.get("y", 0))

        # Get parent bounds
        parent_x, parent_y, parent_w, parent_h = placed[parent_id]

        # Get self bounds
        self_artifact = artifacts[layer_id]
        self_w = self_artifact.width
        self_h = self_artifact.height

        # Parse alignment
        self_align, parent_align = _parse_alignment(align_str)

        # Calculate position
        x = _align_position(
            self_align[0], parent_align[0], self_w, parent_w, parent_x, x_offset
        )
        y = _align_position(
            self_align[1], parent_align[1], self_h, parent_h, parent_y, y_offset
        )

        return (x, y)

    else:
        raise ValueError(f"Unknown anchor type: {anchor_type}")


def _parse_alignment(align_str: str) -> tuple[tuple[str, str], tuple[str, str]]:
    """Parse alignment string into self and parent alignments.

    Format: "c,c" or "se,ee" where:
    - Comma separates self and parent
    - Single char applies to both axes
    - Two chars: first is x-axis, second is y-axis

    Returns:
        ((self_x, self_y), (parent_x, parent_y))
    """
    parts = align_str.split(",")
    if len(parts) != 2:
        raise ValueError(f"Alignment string must be 'self,parent', got '{align_str}'")

    self_str = parts[0].strip()
    parent_str = parts[1].strip()

    # Parse self alignment
    if len(self_str) == 1:
        self_align = (self_str, self_str)  # Apply to both axes
    elif len(self_str) == 2:
        self_align = (self_str[0], self_str[1])
    else:
        raise ValueError(f"Self alignment must be 1-2 chars, got '{self_str}'")

    # Parse parent alignment
    if len(parent_str) == 1:
        parent_align = (parent_str, parent_str)  # Apply to both axes
    elif len(parent_str) == 2:
        parent_align = (parent_str[0], parent_str[1])
    else:
        raise ValueError(f"Parent alignment must be 1-2 chars, got '{parent_str}'")

    # Validate chars
    for char in self_align + parent_align:
        if char not in ("s", "c", "e"):
            raise ValueError(f"Alignment char must be 's', 'c', or 'e', got '{char}'")

    return (self_align, parent_align)


def _align_position(
    self_align: str,
    parent_align: str,
    self_size: int,
    parent_size: int,
    parent_pos: int,
    offset: int,
) -> int:
    """Calculate position for one axis based on alignment.

    Args:
        self_align: 's', 'c', or 'e' (self alignment point)
        parent_align: 's', 'c', or 'e' (parent alignment point)
        self_size: Size of self on this axis
        parent_size: Size of parent on this axis
        parent_pos: Position of parent on this axis
        offset: Additional offset

    Returns:
        Position coordinate for self on this axis.
    """
    # Calculate parent alignment point
    if parent_align == "s":
        parent_point = parent_pos
    elif parent_align == "c":
        parent_point = parent_pos + parent_size // 2
    elif parent_align == "e":
        parent_point = parent_pos + parent_size
    else:
        raise ValueError(f"Invalid parent_align: {parent_align}")

    # Calculate self position so self_align point aligns with parent_point
    if self_align == "s":
        self_pos = parent_point
    elif self_align == "c":
        self_pos = parent_point - self_size // 2
    elif self_align == "e":
        self_pos = parent_point - self_size
    else:
        raise ValueError(f"Invalid self_align: {self_align}")

    return self_pos + offset


def _to_int(value: Any) -> int:
    """Convert value to int, handling Decimal, int, str."""
    if isinstance(value, Decimal):
        return int(value)
    elif isinstance(value, int):
        return value
    elif isinstance(value, str):
        try:
            return int(float(value))  # Handle "10.5" -> 10
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to int")
    elif isinstance(value, float):
        return int(value)
    else:
        raise ValueError(f"Cannot convert {type(value)} to int")
