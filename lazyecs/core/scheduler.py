"""
A minimal system scheduler for LazyECS.

The scheduler is responsible for calling systems in a fixed order
each frame, grouped by phase (e.g. "pre_update", "update", "post_update").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Protocol, Tuple

from .world import World


class System(Protocol):
    """
    Protocol for systems that can be scheduled.

    Any object with a `run(world: World, dt: float) -> None` method
    is considered a valid system.
    """

    def run(self, world: World, dt: float) -> None:
        ...


# Convenience alias for adding simple functions as systems
SystemCallable = Callable[[World, float], None]


@dataclass
class Scheduler:
    """
    A tiny multi-phase scheduler.

    - Systems are grouped into named phases, e.g.:
        "pre_update", "update", "post_update"
    - Within a phase, systems are ordered by an integer `order` value.
    - `run(world, dt)` executes all phases in insertion order.
    """

    _phases: Dict[str, List[Tuple[int, System]]] = field(default_factory=dict)
    _phase_order: List[str] = field(default_factory=list)

    def add_system(self, phase: str, system: System, order: int = 0) -> None:
        """
        Register a system in a given phase.

        Args:
            phase: name of the phase, e.g. "update".
            system: any object with a `run(world, dt)` method.
            order: smaller numbers run earlier within the phase.
        """
        if phase not in self._phases:
            self._phases[phase] = []
            self._phase_order.append(phase)
        self._phases[phase].append((order, system))
        # keep phase list sorted by order
        self._phases[phase].sort(key=lambda pair: pair[0])

    def run(self, world: World, dt: float) -> None:
        """
        Run all systems in all phases in their configured order.
        """
        for phase in self._phase_order:
            systems = self._phases[phase]
            for _, system in systems:
                system.run(world, dt)

    # Convenience for wrapping plain functions as systems -----------------

    def add_function(self, phase: str, func: SystemCallable, order: int = 0) -> None:
        """
        Register a plain function as a system.

        The function must accept (world: World, dt: float).
        """

        class _FuncWrapper:
            def __init__(self, fn: SystemCallable):
                self._fn = fn

            def run(self, world: World, dt: float) -> None:
                self._fn(world, dt)

        self.add_system(phase, _FuncWrapper(func), order=order)
