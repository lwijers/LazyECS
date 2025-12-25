"""
World: central registry of entities, components, and resources.

Game code usually interacts with this class only:
- create/destroy entities
- add/remove/get components
- query entities by component type
- store global resources (like configuration, random generator, etc.)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Tuple, Type, TypeVar

from .types import EntityId
from .store import ComponentStore

T = TypeVar("T")


@dataclass
class World:
    """
    A simple ECS world.

    Responsibilities:
    - Generate unique EntityIds
    - Keep track of which entities are alive
    - Manage per-type ComponentStores
    - Provide a basic query API
    - Store global resources by type

    This class is deliberately small and framework-agnostic.
    """

    _next_entity: int = 1
    _alive: set[EntityId] = field(default_factory=set)
    _stores: Dict[Type[Any], ComponentStore[Any]] = field(default_factory=dict)
    _resources: Dict[Type[Any], Any] = field(default_factory=dict)

    # --- entity lifecycle -----------------------------------------------

    def create(self) -> EntityId:
        """
        Create a new entity and return its id.
        """
        eid = EntityId(self._next_entity)
        self._next_entity += 1
        self._alive.add(eid)
        return eid

    def spawn(self, *components: Any) -> EntityId:
        """
        Convenience helper: create a new entity and optionally attach components.

        Example:
            e = world.spawn(Position(0, 0), Velocity(1, 0))

        Returns:
            The newly created EntityId.
        """
        eid = self.create()
        if components:
            self.add(eid, *components)
        return eid

    def destroy(self, entity: EntityId) -> None:
        """
        Destroy an entity and remove all its components.

        Safe to call multiple times; extra calls are ignored.
        """
        if entity not in self._alive:
            return

        self._alive.remove(entity)

        # Remove from all component stores
        for store in self._stores.values():
            if store.has(entity):
                store.remove(entity)

    def is_alive(self, entity: EntityId) -> bool:
        """
        Returns True if the entity is alive in this world.
        """
        return entity in self._alive

    # --- component store management -------------------------------------

    def _get_store(self, ctype: Type[T]) -> ComponentStore[T]:
        """
        Get or lazily create the ComponentStore for the given component type.
        """
        store = self._stores.get(ctype)
        if store is None:
            store = ComponentStore[T]()
            self._stores[ctype] = store
        return store  # type: ignore[return-value]

    # --- component operations -------------------------------------------

    def add(self, entity: EntityId, *components: Any) -> None:
        """
        Add one or more components to an entity.

        Example:
            world.add(eid, Position(0, 0), Velocity(1, 0))
        """
        if entity not in self._alive:
            raise ValueError(f"Entity {entity!r} is not alive in this world")

        for comp in components:
            ctype = type(comp)
            store = self._get_store(ctype)
            store.add(entity, comp)

    def remove(self, entity: EntityId, *ctypes: Type[Any]) -> None:
        """
        Remove one or more component types from an entity.

        Missing components are ignored.
        """
        for ctype in ctypes:
            store = self._stores.get(ctype)
            if store is not None:
                store.remove(entity)

    def get(self, entity: EntityId, ctype: Type[T]) -> T:
        """
        Get the component of the given type for an entity.

        Raises KeyError if the entity does not have this component type.
        """
        store = self._stores.get(ctype)
        if store is None:
            raise KeyError(f"No components of type {ctype.__name__!r} in world")
        return store.get(entity)

    def try_get(self, entity: EntityId, ctype: Type[T]) -> T | None:
        """
        Get the component of the given type for an entity, or None if missing.
        """
        store = self._stores.get(ctype)
        if store is None:
            return None
        return store.try_get(entity)

    def has(self, entity: EntityId, *ctypes: Type[Any]) -> bool:
        """
        Returns True if the entity has all of the given component types.
        """
        for ctype in ctypes:
            store = self._stores.get(ctype)
            if store is None or not store.has(entity):
                return False
        return True

    # --- queries --------------------------------------------------------

    def query(self, *ctypes: Type[Any]) -> Iterable[Tuple[EntityId, Tuple[Any, ...]]]:
        """
        Iterate over entities that have all of the given component types.

        Yields (entity_id, (comp1, comp2, ...)).

        This is a very simple "all_of" query, optimized by iterating over
        the smallest ComponentStore and checking the rest.
        """
        if not ctypes:
            return []

        # Pick the smallest store to iterate as the "driver"
        stores: List[ComponentStore[Any]] = []
        for ctype in ctypes:
            store = self._stores.get(ctype)
            if store is None:
                # If any component type has no instances, the query is empty
                return []
            stores.append(store)

        # Sort stores by size so we iterate the smallest first
        stores_with_types = list(zip(ctypes, stores))
        stores_with_types.sort(key=lambda pair: len(pair[1]))
        driver_type, driver_store = stores_with_types[0]
        rest = stores_with_types[1:]

        def _iter() -> Iterable[Tuple[EntityId, Tuple[Any, ...]]]:
            for eid, first_comp in driver_store.items():
                # Skip dead entities (in case of stale data)
                if eid not in self._alive:
                    continue

                comps: List[Any] = [first_comp]
                ok = True
                for ctype, store in rest:
                    if not store.has(eid):
                        ok = False
                        break
                    comps.append(store.get(eid))
                if ok:
                    yield eid, tuple(comps)

        return _iter()

    def query_entities(self, *ctypes: Type[Any]) -> Iterable[EntityId]:
        """
        Iterate over entities that have all of the given component types,
        but only yield the entity ids (no component tuple).

        This can be a bit nicer to use when you don't need the components directly.
        """
        for eid, _ in self.query(*ctypes):
            yield eid

    # --- resources ------------------------------------------------------

    def set_resource(self, rtype: Type[T], resource: T) -> None:
        """
        Store a global resource by its type.

        Common example: random generator, configuration, event bus, etc.
        """
        self._resources[rtype] = resource

    def get_resource(self, rtype: Type[T]) -> T:
        """
        Retrieve a global resource by its type.

        Raises KeyError if not present.
        """
        return self._resources[rtype]

    def try_get_resource(self, rtype: Type[T]) -> T | None:
        """
        Retrieve a global resource by its type, or None if missing.
        """
        return self._resources.get(rtype)  # type: ignore[return-value]

    # --- debug helpers --------------------------------------------------

    @property
    def alive_entities(self) -> Iterable[EntityId]:
        """
        Iterate over all alive entity ids.
        """
        return iter(self._alive)

    def stats(self) -> Mapping[str, Any]:
        """
        Return a small diagnostic dict about the world:
        - entity_count
        - component_types (with counts)
        """
        return {
            "entity_count": len(self._alive),
            "component_types": {
                ctype.__name__: len(store) for ctype, store in self._stores.items()
            },
        }
