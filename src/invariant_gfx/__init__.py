"""invariant_gfx: A deterministic, DAG-based graphics engine built on Invariant."""

from invariant.registry import OpRegistry

__version__ = "0.1.0"

__all__ = ["register_core_ops", "__version__"]


def register_core_ops(registry: OpRegistry) -> None:
    """Register all core graphics operations in the OpRegistry.

    Args:
        registry: The OpRegistry instance to register operations in.
    """
    from invariant_gfx.ops import OPS

    registry.register_package("gfx", OPS)
