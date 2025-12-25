# tests/test_world_basic.py

import pytest

from lazyecs import World  # let op: pakketnaam moet matchen met jouw map/__init__


class Position:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class Velocity:
    def __init__(self, vx: float, vy: float) -> None:
        self.vx = vx
        self.vy = vy


def test_create_and_destroy_entity():
    w = World()

    e1 = w.create()
    e2 = w.create()

    assert w.is_alive(e1)
    assert w.is_alive(e2)
    assert e1 != e2

    w.destroy(e1)
    assert not w.is_alive(e1)
    assert w.is_alive(e2)


def test_add_get_and_remove_component():
    w = World()
    e = w.create()

    pos = Position(1.0, 2.0)
    w.add(e, pos)

    # get
    got = w.get(e, Position)
    assert got is pos
    assert (got.x, got.y) == (1.0, 2.0)

    # has
    assert w.has(e, Position)

    # remove
    w.remove(e, Position)
    assert not w.has(e, Position)
    assert w.try_get(e, Position) is None
    with pytest.raises(KeyError):
        _ = w.get(e, Position)


def test_query_with_two_components():
    w = World()

    e1 = w.create()
    e2 = w.create()
    e3 = w.create()

    w.add(e1, Position(0, 0), Velocity(1, 0))
    w.add(e2, Position(10, 0))             # alleen Position
    w.add(e3, Velocity(0, 1))              # alleen Velocity

    result = list(w.query(Position, Velocity))
    assert len(result) == 1

    eid, (pos, vel) = result[0]
    assert eid == e1
    assert isinstance(pos, Position)
    assert isinstance(vel, Velocity)


def test_destroy_removes_all_components():
    w = World()
    e = w.create()
    w.add(e, Position(0, 0), Velocity(1, 0))

    w.destroy(e)

    assert not w.is_alive(e)
    assert w.try_get(e, Position) is None
    assert w.try_get(e, Velocity) is None

    # query should not return destroyed entity
    assert list(w.query(Position, Velocity)) == []


def test_stats_reports_components_and_entities():
    w = World()
    e1 = w.create()
    e2 = w.create()

    w.add(e1, Position(0, 0))
    w.add(e2, Position(1, 1), Velocity(1, 0))

    s = w.stats()
    assert s["entity_count"] == 2
    assert s["component_types"]["Position"] == 2
    assert s["component_types"]["Velocity"] == 1
