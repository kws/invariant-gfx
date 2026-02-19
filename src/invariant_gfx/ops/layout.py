"""gfx:layout operation - content-sized arrangement engine (row/column flow)."""

from decimal import Decimal
from typing import Any

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def layout(manifest: dict[str, Any]) -> ICacheable:
    """Arrange items in a flow (row or column) with content-sized output.

    Args:
        manifest: Must contain:
            - 'direction': "row" or "column" (main axis flow direction)
            - 'align': "s", "c", or "e" (cross-axis alignment)
            - 'gap': Decimal (spacing between items in pixels)
            - 'items': List[str] (ordered list of upstream node IDs)
            - Artifacts for each item ID (as ImageArtifact)

    Returns:
        ImageArtifact sized to the tight bounding box of arranged items (RGBA mode).

    Raises:
        KeyError: If required keys are missing.
        ValueError: If direction/align values are invalid or items cannot be found.
    """
    if "direction" not in manifest:
        raise KeyError("gfx:layout requires 'direction' in manifest")
    if "align" not in manifest:
        raise KeyError("gfx:layout requires 'align' in manifest")
    if "gap" not in manifest:
        raise KeyError("gfx:layout requires 'gap' in manifest")
    if "items" not in manifest:
        raise KeyError("gfx:layout requires 'items' in manifest")

    direction = manifest["direction"]
    align = manifest["align"]
    gap_val = manifest["gap"]
    items = manifest["items"]

    # Validate direction
    if direction not in ("row", "column"):
        raise ValueError(f"direction must be 'row' or 'column', got '{direction}'")

    # Validate align
    if align not in ("s", "c", "e"):
        raise ValueError(f"align must be 's', 'c', or 'e', got '{align}'")

    # Convert gap to int
    if isinstance(gap_val, Decimal):
        gap = int(gap_val)
    elif isinstance(gap_val, (int, str)):
        gap = int(gap_val)
    else:
        raise ValueError(f"gap must be Decimal, int, or str, got {type(gap_val)}")

    if gap < 0:
        raise ValueError(f"gap must be non-negative, got {gap}")

    # Validate items
    if not isinstance(items, list):
        raise ValueError(f"items must be a list, got {type(items)}")

    if len(items) == 0:
        raise ValueError("items must contain at least one item")

    # Extract artifacts for each item
    artifacts: list[ImageArtifact] = []
    for item_id in items:
        if not isinstance(item_id, str):
            raise ValueError(f"item ID must be a string, got {type(item_id)}")

        if item_id not in manifest:
            raise KeyError(
                f"Item '{item_id}' not found in manifest. "
                f"Make sure it's listed in node.deps."
            )

        artifact = manifest[item_id]
        if not isinstance(artifact, ImageArtifact):
            raise ValueError(
                f"Item '{item_id}' must be ImageArtifact, got {type(artifact)}"
            )

        artifacts.append(artifact)

    # Calculate layout dimensions
    if direction == "row":
        # Main axis: horizontal
        # Width = sum of item widths + gaps between items
        total_width = sum(art.width for art in artifacts) + gap * (len(artifacts) - 1)
        # Height = max of item heights
        total_height = max(art.height for art in artifacts) if artifacts else 0
    else:  # column
        # Main axis: vertical
        # Width = max of item widths
        total_width = max(art.width for art in artifacts) if artifacts else 0
        # Height = sum of item heights + gaps between items
        total_height = sum(art.height for art in artifacts) + gap * (len(artifacts) - 1)

    if total_width <= 0 or total_height <= 0:
        raise ValueError(
            f"Layout dimensions invalid: {total_width}x{total_height}. "
            f"All items must have positive dimensions."
        )

    # Create canvas
    canvas = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))

    # Place items
    if direction == "row":
        # Horizontal arrangement
        x = 0
        for artifact in artifacts:
            # Calculate y position based on cross-axis alignment
            if align == "s":
                y = 0
            elif align == "c":
                y = (total_height - artifact.height) // 2
            else:  # align == "e"
                y = total_height - artifact.height

            # Paste item
            canvas.paste(artifact.image, (x, y), artifact.image)

            # Move to next position
            x += artifact.width + gap

    else:  # column
        # Vertical arrangement
        y = 0
        for artifact in artifacts:
            # Calculate x position based on cross-axis alignment
            if align == "s":
                x = 0
            elif align == "c":
                x = (total_width - artifact.width) // 2
            else:  # align == "e"
                x = total_width - artifact.width

            # Paste item
            canvas.paste(artifact.image, (x, y), artifact.image)

            # Move to next position
            y += artifact.height + gap

    return ImageArtifact(canvas)
