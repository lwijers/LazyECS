"""
Shared type definitions for LazyECS.
"""

from typing import NewType

# For now, EntityId is just an int. Using NewType makes the intent explicit
# without adding runtime overhead.
EntityId = NewType("EntityId", int)
