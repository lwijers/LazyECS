LazyECS is a small, clean and reusable Entity-Component-System (ECS) framework written in Python.
It is intentionally minimal, well-documented, and designed to stay out of your way while giving you the power and structure of a real ECS architecture.

The goal is simple:

A lightweight ECS that is easy to understand, easy to extend, and pleasant to use in games, simulations, UI systems and prototypes.

LazyECS is used in personal projects ranging from game simulations to custom UI toolkits and Pygame experiments.

✨ Features

Minimal, well-designed ECS core

Entities as integer IDs

Components as plain Python objects

Dense component storage with swap-remove

Fast, type-based queries

No heavy framework or magic involved

Modular Scheduler

Multi-phase update loop: pre_update, update, post_update, etc.

Systems ordered within each phase

Works great with Pygame or any game loop

Ergonomic API

world.spawn(...) helper

world.query(ComponentA, ComponentB)

Easy to test and reason about

No dependencies

Pure Python

Works with CPython (incl. Python 3.12–3.14)

Compatible with pygame-ce for demos

100% optional extras

LazyECS is deliberately small: you can layer your own event bus, UI systems or game logic on top.

📦 Installation

LazyECS is not on PyPI (yet), but is easy to use locally:

pip install -e .


Or simply drop the lazyecs/ folder into your project.

🧠 Core Concepts
World

The central data structure.
It stores:

Entity IDs

Component sets

Resources (if you choose to add them)

You interact with it using:

e = world.create()
world.add(e, Position(0, 0), Velocity(1, 0))
world.get(e, Position)
world.query(Position, Velocity)
world.destroy(e)

Components

Plain Python objects (dataclasses recommended):

@dataclass
class Position:
    x: float
    y: float

Systems

Regular classes or functions with a run(world, dt) method.

Systems read and modify component data.
They do not know about each other → clean separation.

Scheduler

Coordinates system execution per frame.

Example:

scheduler.add_system("pre_update", InputSystem(), order=0)
scheduler.add_system("update", MovementSystem(), order=0)
scheduler.add_system("update", CollisionSystem(), order=10)
scheduler.add_system("render", RenderSystem(screen), order=0)


When you call:

scheduler.run(world, dt)


…all systems run in phase and order.

🚀 Demo — Bouncing Circles (Pygame)

LazyECS includes a fully working Pygame demo showing how the ECS fits naturally into a real update loop.

Run it with:

python demo_pygame_ecs.py


Features:

Spawn bouncing circles with left mouse click

ESC to quit

Uses Position + Velocity + Circle + Color components

Systems for:

Input handling

Movement

Boundary bouncing

Rendering

This demo is intentionally straightforward and meant as a starting point for more advanced systems.

🧪 Tests

LazyECS ships with a set of small, focused tests under tests/:

test_world_basic.py

test_store_basic.py

test_scheduler_basic.py

Run all tests with:

pytest -q


These tests give you confidence when refactoring or extending the ECS.

🔧 Project Structure
lazyecs/
  __init__.py
  core/
    world.py
    store.py
    scheduler.py
    types.py
tests/
  test_world_basic.py
  test_store_basic.py
  test_scheduler_basic.py
demo_pygame_ecs.py
main.py
README.md
