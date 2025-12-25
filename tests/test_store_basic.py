# tests/test_store_basic.py

from lazyecs import ComponentStore
from lazyecs.core.types import EntityId


class Dummy:
    def __init__(self, value: int) -> None:
        self.value = value


def make_eid(n: int) -> EntityId:
    return EntityId(n)


def test_add_and_get_component_store():
    store = ComponentStore[Dummy]()

    e1 = make_eid(1)
    e2 = make_eid(2)

    d1 = Dummy(10)
    d2 = Dummy(20)

    store.add(e1, d1)
    store.add(e2, d2)

    assert store.get(e1) is d1
    assert store.get(e2) is d2
    assert store.has(e1)
    assert store.has(e2)
    assert len(store) == 2


def test_overwrite_existing_component():
    store = ComponentStore[Dummy]()
    e = make_eid(1)

    d1 = Dummy(10)
    d2 = Dummy(42)

    store.add(e, d1)
    store.add(e, d2)  # overwrite

    assert len(store) == 1
    assert store.get(e) is d2
    assert store.get(e).value == 42


def test_remove_uses_swap_trick_and_keeps_dense():
    store = ComponentStore[Dummy]()

    e1 = make_eid(1)
    e2 = make_eid(2)
    e3 = make_eid(3)

    store.add(e1, Dummy(1))
    store.add(e2, Dummy(2))
    store.add(e3, Dummy(3))

    # we don't know internal order, but length is 3
    assert len(store) == 3

    # remove middle entity (depending on layout)
    store.remove(e2)
    assert not store.has(e2)
    assert len(store) == 2

    # still can access others
    assert store.has(e1)
    assert store.has(e3)


def test_try_get_and_entities_iteration():
    store = ComponentStore[Dummy]()
    e1 = make_eid(1)
    e2 = make_eid(2)

    store.add(e1, Dummy(1))
    store.add(e2, Dummy(2))

    assert store.try_get(e1) is not None
    assert store.try_get(make_eid(99)) is None

    entities = set(store.entities())
    assert entities == {e1, e2}
