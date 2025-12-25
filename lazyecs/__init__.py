"""
LazyECS - a tiny, reusable Entity Component System core.

This package is intentionally framework-agnostic:
it does not know about rendering, input, or any specific game engine.
"""

from .core.types import EntityId
from .core.world import World
from .core.store import ComponentStore
from .core.scheduler import Scheduler

__all__ = [
    "EntityId",
    "World",
    "ComponentStore",
    "Scheduler",
]
