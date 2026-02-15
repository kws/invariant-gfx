# invariant_gfx

A deterministic, functional graphics pipeline built on **Invariant**. invariant_gfx allows developers to build complex visual assets (icons, badges, dynamic UI components, Stream Deck buttons, data visualizations) by plugging together reusable "pipeline parts" in a DAG-based system.

Unlike traditional imperative rendering (where you draw lines on a mutable canvas), invariant_gfx is **functional**: every layer, mask, or composition is an immutable **Artifact** produced by a pure function.

## Features

- **Aggressive Caching**: Identical visual operations (rendering the same text, compositing the same layers) execute only once
- **Deduplication**: The same icon rendered at the same size is reused across all buttons
- **Reproducibility**: Bit-for-bit identical outputs across runs and architectures
- **Functional Rendering**: Immutable artifacts flow through pure function operations
- **Smart Layout**: Ops can inspect upstream artifact dimensions to calculate positions dynamically
- **Anchor-Based Composition**: Position layers relative to previously-placed named layers
- **Content-Sized Layout**: Flow-based arrangement (row/column) with automatic sizing

## Relationship to Invariant

invariant_gfx is a **child project** of Invariant:

- **Invariant (Parent)**: Provides the DAG execution engine, caching infrastructure, and core protocols. Invariant has **NO image awareness**—it is domain-agnostic.
- **invariant_gfx (Child)**: Provides graphics-specific Ops (render_text, composite, render_svg) and Artifacts (ImageArtifact, BlobArtifact). All image/Pillow concerns live here.

## Op Standard Library

invariant_gfx provides a standard library of graphics operations organized into four groups:

### Group A: Sources (Data Ingestion)
- `fetch_resource`: Downloads external assets (images, fonts, SVGs) with version-based caching
- `create_solid`: Generates solid color or gradient textures

### Group B: Transformers (Rendering)
- `render_svg`: Converts SVG blobs into raster artifacts (sandboxed, no network access)
- `render_text`: Creates tight-fitting "Text Pill" artifacts
- `render_shape`: Renders primitive vector shapes (rect, rounded_rect, ellipse, line)

### Group C: Composition (Combiners)
- `composite`: Fixed-size composition engine with anchor-based positioning
- `layout`: Content-sized arrangement engine (row/column flow)

### Group D: Type Conversion (Casting)
- `blob_to_image`: Parses raw binary data (PNG, JPEG, WEBP) into ImageArtifact

For detailed Op specifications, see [docs/architecture.md](docs/architecture.md).

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd invariant_gfx

# Install dependencies
poetry install
```

**Note**: This project depends on a local development version of Invariant. The dependency is configured in `pyproject.toml` as a file path reference.

## Quick Start

```python
from invariant import Node
from invariant_gfx import Pipeline  # Pipeline wrapper (may move to invariant core in future)
from decimal import Decimal

# Define render input
render_input = {
    "font": "Inter",
    "icon": "lucide:thermometer",
    "background": "http://example.com/someimage.jpg",
    "temperature": "23.5",
    "height": 122,
    "width": 122,
}

# Build the graph
graph = {
    "input": Node(
        op_name="identity",
        params={"value": render_input},
        deps=[]
    ),
    
    "background_image": Node(
        op_name="fetch_resource",
        params={
            "url": render_input["background"],
            "version": 1,
        },
        deps=["input"]
    ),
    
    "text_render": Node(
        op_name="render_text",
        params={
            "text": render_input["temperature"],
            "font": "Inter",
            "size": Decimal("11.5"),
            "color": "#FFF"
        },
        deps=["input"]
    ),
    
    # ... more nodes for composition ...
}

# Execute the pipeline
pipeline = Pipeline(decimal_prec=2)
artifacts = pipeline.executor.execute(graph)
final_image = artifacts["final"]
```

For a complete example, see the Thermometer pipeline in [docs/architecture.md](docs/architecture.md).

## Status

**Architecture**: Complete and documented

**Implementation**: In progress
- Op standard library specification: ✅ Complete
- Artifact types (ImageArtifact, BlobArtifact): ⏳ Pending
- Composite and layout algorithms: ✅ Designed
- anchor() DSL helper: ✅ Designed
- Actual Op implementations: ⏳ Pending
- Pipeline wrapper class: ⏳ Pending
- Integration with JustMyType/JustMyResource: ⏳ Pending

## Architecture

invariant_gfx uses Invariant's two-phase execution model:

1. **Phase 1: Context Resolution** - Builds input manifests for each node, calculates stable hashes
2. **Phase 2: Action Execution** - Executes operations or retrieves from cache

For detailed architecture documentation, see [docs/architecture.md](docs/architecture.md).

For AI agents working with this codebase, see [AGENTS.md](AGENTS.md).

## Development

```bash
# Run tests
poetry run pytest

# Run linting
poetry run ruff check src/ tests/

# Format code
poetry run ruff format src/ tests/
```

## License

MIT License - see [LICENSE](LICENSE) for details.

