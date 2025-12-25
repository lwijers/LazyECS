"""
Component storage for LazyECS.

A ComponentStore keeps components of a single type in dense arrays,
allowing O(1) add/remove/get by EntityId and efficient iteration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Generic, Iterable, Iterator, List, Tuple, TypeVar

from .types import EntityId

T = TypeVar("T")


@dataclass
class ComponentStore(Generic[T]):
    """
    Dense storage for components of a single type.

    Internally:
      - _data:   list of components
      - _entities: list of entity ids (parallel to _data)
      - _index: map from entity id -> index in _data/_entities

    This is not meant to be used directly in game code; you normally
    interact through World.add/get/remove/query, which wraps these stores.
    """

    _data: List[T] = field(default_factory=list)
    _entities: List[EntityId] = field(default_factory=list)
    _index: Dict[EntityId, int] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self._data)

    # --- basic CRUD -----------------------------------------------------

    def add(self, entity: EntityId, component: T) -> None:
        """
        Add or replace a component for this entity.

        If the entity already has this component type, it is overwritten.
        """
        if entity in self._index:
            idx = self._index[entity]
            self._data[idx] = component
            return

        idx = len(self._data)
        self._data.append(component)
        self._entities.append(entity)
        self._index[entity] = idx

    def remove(self, entity: EntityId) -> None:
        """
        Remove the component for an entity.

        Does nothing if the entity does not have this component type.
        """
        idx = self._index.pop(entity, None)
        if idx is None:
            return

        last_idx = len(self._data) - 1
        if idx != last_idx:
            # Move last element into removed slot to keep storage dense
            last_comp = self._data[last_idx]
            last_entity = self._entities[last_idx]

            self._data[idx] = last_comp
            self._entities[idx] = last_entity
            self._index[last_entity] = idx

        # Remove last element
        self._data.pop()
        self._entities.pop()

    def get(self, entity: EntityId) -> T:
        """
        Get the component for an entity.

        Raises KeyError if the entity does not have this component type.
        """
        idx = self._index[entity]
        return self._data[idx]

    def try_get(self, entity: EntityId) -> T | None:
        """
        Get the component or None if entity does not have it.
        """
        idx = self._index.get(entity)
        if idx is None:
            return None
        return self._data[idx]

    def has(self, entity: EntityId) -> bool:
        """
        Returns True if the entity has this component type.
        """
        return entity in self._index

    # --- iteration helpers ----------------------------------------------

    def items(self) -> Iterable[Tuple[EntityId, T]]:
        """
        Iterate over (entity, component) pairs.
        """
        for e, c in zip(self._entities, self._data):
            yield e, c

    def values(self) -> Iterable[T]:
        """
        Iterate over components only.
        """
        return iter(self._data)

    def entities(self) -> Iterable[EntityId]:
        """
        Iterate over entities that have this component type.
        """
        return iter(self._entities)

    def __iter__(self) -> Iterator[Tuple[EntityId, T]]:
        return iter(self.items())
