# **invariant\_icon: The Functional Graphics Pipeline**

**invariant\_icon** is a deterministic, DAG-based graphics engine built on **Invariant**. It allows developers to build complex visual assets (like Stream Deck buttons, dynamic badges, or data visualizations) by plugging together reusable "pipeline parts."

Unlike traditional imperative rendering (where you draw lines on a mutable canvas), invariant\_icon is **functional**: every layer, mask, or composition is an immutable **Artifact** produced by a pure function.

## **1\. Core Philosophy**

### **The "Smart Op" Model**

Layout logic lives **inside** the Graph, not in a pre-processing step.

* **Traditional:** Calculate that "Hello" is 50px wide, then tell the draw command to place it at x=25.  
* **Invariant GFX:** Tell the composite Op to align the "Hello" artifact to center. The Op resolves the pixel math at runtime based on the actual size of the upstream inputs.

### **Explicit Data Flow (The "Switchboard")**

There is no "Global Context" or "Environment Variables."

* **Rule:** If a node needs data (like a URL or a temperature value), that data must be the output of an upstream **Identity Node**.  
* **Benefit:** The graph is hermetic. You can visualize exactly where every piece of data comes from.

### **Strict Numeric Policy**

All layout inputs (offsets, font sizes, opacity) use decimal.Decimal or int to ensure bit-level precision across architectures.

## **2\. Data Transfer Objects (Artifacts)**

We standardise on two Artifact types to ensure interoperability between all Ops.

### **ImageArtifact**

The universal visual primitive passed between nodes.

* **Content:** A PIL.Image (Standardized to **RGBA**).  
* **Serialization:** Canonical **PNG** (Level 1 compression, metadata stripped).  
* **Identity:** SHA-256 of the PNG bytes.  
* **Properties:** Exposes .width and .height to downstream Ops.

### **BlobArtifact**

Container for raw binary resources.

* **Content:** Raw bytes.  
* **Use Cases:** SVG source files, TTF font binaries, downloaded assets.

## **3\. Operation Registry & Extensibility**

invariant\_icon relies on the core **Invariant OpRegistry** to map string identifiers to executable Python logic. This decoupling allows the pipeline to be purely declarative while supporting infinite extensibility.

### **The Registry Pattern**

The pipeline does not contain code; it contains **references**. At runtime, the Executor looks up the op\_name in the Registry.

\# System initialization  
registry \= OpRegistry()

\# 1\. Register Standard Library (Core Ops)  
invariant\_icon.register\_core\_ops(registry) 

\# 2\. Register Custom/Application Ops  
registry.register("myapp:custom\_filter", my\_custom\_filter\_op)

### **Namespacing Conventions**

To prevent collisions in extensible pipelines, we enforce a namespacing convention.

1. **Core Ops (op\_name)**: Reserved for the Standard Library.  
   * Examples: composite, render\_text, fetch\_resource.  
2. **Extension Ops (namespace:op\_name)**: For application-specific logic.  
   * Examples: filters:gaussian\_blur, analytics:render\_sparkline.

## **4\. The Op Standard Library**

These Ops form the "Instruction Set" of the graphics engine.

### **Group A: Sources (Data Ingestion)**

#### **fetch\_resource**

Handles external assets (images, fonts, SVGs) while preserving the Invariant contracts.

* **Inputs:**  
  * url: Source URL.  
  * version: **Mandatory** cache-buster.  
* **Behavior:** If version matches the cache, the network request is skipped. Outputs a BlobArtifact.

#### **create\_solid**

Generates a solid color or gradient texture.

* **Inputs:**  
  * size: Tuple\[Decimal, Decimal\].  
  * color: RGBA Tuple.  
* **Output:** ImageArtifact.

### **Group B: Transformers (Rendering)**

#### **render\_svg**

Converts SVG blobs into raster artifacts.

* **Inputs:**  
  * svg\_content: BlobArtifact (The XML).  
  * width / height: Decimal (Target raster size).  
  * assets: Dict\[str, ImageArtifact\] (Images to inject into the SVG, replacing hrefs).  
  * fonts: Dict\[str, BlobArtifact\] (Fonts to inject).  
* **Security:** The renderer is sandboxed (no network access). All dependencies must be injected via assets or fonts.

#### **render\_text**

Creates a tight-fitting "Text Pill" artifact.

* **Inputs:**  
  * text: String content.  
  * font\_blob: BlobArtifact (Actual font file).  
  * size: Decimal (Font size).  
  * color: RGBA Tuple.

#### **render\_shape**

Renders primitive vector shapes directly to an ImageArtifact (wrapping Pillow/ImageDraw).

* **Inputs:**  
  * shape: Enum ("rect", "rounded\_rect", "ellipse", "line").  
  * size: Tuple\[Decimal, Decimal\].  
  * fill: RGBA Tuple (Optional).  
  * stroke: RGBA Tuple (Optional).  
  * stroke\_width: Decimal.  
  * radius: Decimal (For rounded\_rect).

### **Group C: Composition (Combiners)**

#### **composite**

Fixed-size composition engine. Stacks multiple layers onto a fixed-size canvas where each layer anchors to a previously-placed named layer.

* **Inputs:**  
  * layers: List\[LayerSpec\].
    * The first layer defines the canvas size (must have fixed dimensions).
    * Subsequent layers reference previously-placed layers by `id` using the `anchor()` function.
    * No special "canvas" or "background" concept - everything references named layers.

**The LayerSpec & Blend Modes:**

class LayerSpec(TypedDict):  
    ref: ImageArtifact  
    id: str | None        \# Optional name, required if other layers reference this one
    anchor: AnchorSpec     \# Position via anchor() function (see anchor() documentation below)
    mode: str \= "normal"   \# Photoshop-style Blending: 'normal', 'multiply', 'screen', 'overlay', 'darken', 'lighten', 'add'  
    opacity: Decimal \= 1.0

**The `anchor()` Function:**

Positions a layer relative to a previously-placed named layer.

**Note:** `anchor()` is an invariant_gfx DSL helper function (not an Invariant primitive). It returns an `AnchorSpec` object that is used in the `composite` op's LayerSpec.

* **Syntax**: `anchor(layer_id, 'self_align,ref_align', x=offset, y=offset)`
* **Parameters**:
  * `layer_id`: String ID of a previously-placed layer (mandatory - no canvas concept)
  * `alignment`: Comma-separated pair using `s` (start), `c` (center), `e` (end)
    * First value = self alignment (which point on *this* layer)
    * Second value = reference alignment (which point on the *referenced* layer)
    * Examples:
      * `'c,c'` = center of self aligns to center of reference (centered)
      * `'s,e'` = start of self aligns to end of reference (outside placement / badge)
      * `'e,e'` = end of self aligns to end of reference (right/bottom aligned)
      * `'se,ee'` = on x-axis: self-start to ref-end; on y-axis: self-end to ref-end (text following on same baseline)
  * `x`, `y`: Optional Decimal pixel offsets applied after alignment

**Examples**:
* `anchor('bg', 'c,c')` - center element on 'bg' layer
* `anchor('bg', 'e,e')` - bottom-right align to 'bg' layer
* `anchor('bg', 'c,c', y=5)` - center on 'bg', shifted 5px down
* `anchor('text1', 'se,ee', x=5)` - place immediately after 'text1' on the same baseline with 5px gap

#### **layout**

Content-sized arrangement engine. Arranges items in a flow (row or column) when the output size is not known upfront.

* **Inputs:**  
  * direction: `"row"` or `"column"` (main axis flow direction)
  * align: Cross-axis alignment using `s` (start), `c` (center), or `e` (end)
  * gap: Decimal spacing between items
  * items: Ordered list of ImageArtifact references
* **Output**: ImageArtifact sized to the tight bounding box of the arranged items
* **Key difference from composite**: No anchoring to named layers; items flow sequentially. Output size is derived from content, not fixed.

### **Group D: Type Conversion (Casting)**

Ops that transform raw data into usable artifacts without changing the visual content.

#### **blob\_to\_image**

Parses raw binary data (PNG, JPEG, WEBP) into a decoded ImageArtifact.

* **Inputs:**  
  * blob: BlobArtifact (The raw bytes).  
* **Output:** ImageArtifact.  
* **Purpose:** Allows a downloaded raster image to be used in composite (which requires dimensions) or as an asset in render\_svg.

## **5\. Missing Upstream Features (Gaps in Invariant)**

The following features are needed by invariant_gfx but are **not yet implemented** in Invariant. These gaps should be clearly understood when working with the architecture:

| Feature | Description | Impact on invariant_gfx |
| :---- | :---- | :---- |
| **Expression Evaluation** | `${...}` template syntax in Node params (e.g., `${input.background}`, `${Decimal(input.width) * Decimal('0.8')}`) | Currently cannot reference upstream artifacts or external context in params. Workaround: Use identity nodes or literal values. |
| **Context Injection** | External input data passed to graph execution (e.g., `pipeline.render(graph, context={"input": render_input})`) | Currently cannot inject external data. Workaround: Use identity nodes at graph root. |
| **Pipeline Class** | Ergonomic wrapper around Executor with context support | Currently must use Executor directly. Workaround: Implement Pipeline wrapper in invariant_gfx (may later move to invariant core). |
| **List/Dict Cacheable Types** | Composite data structures implementing ICacheable | Currently cannot pass lists/dicts of artifacts in params. Workaround: Pending implementation. |
| **Op Namespace Enforcement** | Formal `namespace:op_name` convention with validation | Currently OpRegistry accepts any string but has no namespace validation. Workaround: Manual convention enforcement. |

**Current Status:** The example in Section 6 shows the intended API with expression evaluation and context injection, but these features are marked with TODO comments indicating they are not yet available.

## **6\. Pipeline Example: The Thermometer**

This example demonstrates the **layout** and **composite** ops working together: `layout` arranges content-sized elements, then `composite` places the result onto a fixed-size background.

```python
from invariant import Node
from invariant_gfx import Pipeline  # Pipeline wrapper (may move to invariant core in future)
from decimal import Decimal

# Note: Expression evaluation (${...}) and context injection are planned features
# not yet implemented in Invariant. Until then, use identity nodes for external inputs.
render_input = {
    "font": "Inter",
    "icon": "lucide:thermometer",
    "background": "http://example.com/someimage.jpg",
    "temperature": f"{temp:.1f}",
    "height": 122,
    "width": 122,
}

graph = {  
    # --- 1. Context Input (Identity Node) ---
    # Until context injection is implemented, external data must come via identity nodes
    "input": Node(
        op_name="identity",
        params={"value": render_input},  # In future: context={"input": render_input}
        deps=[]
    ),
    
    # --- 2. Asset Loading ---  
    "background_image": Node(  
        op_name="fetch_resource",  
        params={  
            # TODO: Expression evaluation (${input.background}) not yet implemented
            # For now, use literal values or identity node outputs
            "url": render_input["background"],  # Future: "${input.background}"
            "version": 1,  # This is a 'cache buster' since this op is only re-run if the inputs change
        },  
        deps=["input"]  
    ),  

    "background_image_render": Node(
        op_name="resize",
        params={
            # TODO: Expression evaluation not yet implemented
            "image": None,  # Future: "${background_image.data}" - would reference upstream artifact
            "width": render_input["width"],  # Future: "${input.width}"
            "height": render_input["height"],  # Future: "${input.height}"
        },
        deps=["input", "background_image"]
    ),

    "thermo_icon_src": Node(  
        op_name="svg_icon",  # Uses resolution mechanism mentioned in docs/icons.md - we'll probably call that JustMyResource
        params={
            # TODO: Expression evaluation not yet implemented
            "ref": render_input["icon"]  # Future: "${input.icon}"
        },  
        deps=["input"]  
    ),

    # --- 3. Processing ---  
    "text_render": Node(  
        op_name="render_text",  
        params={  
            # TODO: Expression evaluation not yet implemented
            "text": render_input["temperature"],  # Future: "${input.temperature}"
            "font": "Inter",  # Uses JustMyType to resolve the correct font https://github.com/kws/justmytype
            "size": Decimal("11.5"),  
            "color": "#FFF"  
        },  
        deps=["input"]  
    ),

    "thermo_icon": Node(  
        op_name="render_svg",  
        params={  
            # TODO: Expression evaluation not yet implemented
            "svg_content": None,  # Future: "${thermo_icon_src.svg_string}" - would reference upstream artifact
            "width": Decimal(str(int(render_input["width"]) * 0.8)),  # Future: "${Decimal(input.width) * Decimal('0.8')}"
            "height": Decimal(str(int(render_input["height"]) * 0.8)),  # Future: "${Decimal(input.height) * Decimal('0.8')}"
        },  
        deps=["thermo_icon_src"]  
    ),

    # --- 4. Content Layout (Content-Sized) ---  
    "gauge_layout": Node(
        op_name="layout",
        params={
            "direction": "column",
            "align": "c",
            "gap": Decimal("5"),
            # TODO: Expression evaluation and List cacheable type not yet implemented
            # Future: items=["${thermo_icon.image}", "${text_render.image}"]
            # For now, would need to construct list from upstream artifacts
            "items": []  # Placeholder - actual implementation pending
        },
        deps=["thermo_icon", "text_render"]
    ),

    # --- 5. Final Composition (Fixed-Size) ---  
    "final": Node(
        op_name="composite",
        params={
            # TODO: Expression evaluation and List/Dict cacheable types not yet implemented
            # Future: layers=[{...}, {...}] with ${...} expressions
            "layers": []  # Placeholder - actual implementation pending
        },
        deps=["background_image_render", "gauge_layout"]
    )  
}  

# Pipeline wrapper (may move to invariant core in future)
# TODO: Context injection not yet implemented - currently Executor.execute() only accepts graph
pipeline = Pipeline(decimal_prec=2)  # Ergonomic wrapper around Executor with cache location and default decimal precision
# Future: final_image = pipeline.render(graph, context={"input": render_input})
# Current: artifacts = pipeline.executor.execute(graph); final_image = artifacts["final"]
```
