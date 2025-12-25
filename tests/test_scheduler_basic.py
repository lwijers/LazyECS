# tests/test_scheduler_basic.py

from lazyecs import World, Scheduler


class CounterSystem:
    def __init__(self, tag: str, log: list[str]) -> None:
        self.tag = tag
        self.log = log

    def run(self, world: World, dt: float) -> None:
        self.log.append(self.tag)


def test_scheduler_runs_systems_in_phase_order():
    world = World()
    sched = Scheduler()

    log: list[str] = []

    # Add systems in the phase order we conceptually want:
    #   pre_update -> update -> post_update
    # The scheduler's phase execution order is "first time a phase is seen".
    sched.add_system("pre_update", CounterSystem("pre1", log), order=0)
    sched.add_system("update", CounterSystem("update1", log), order=10)
    sched.add_system("update", CounterSystem("update0", log), order=0)
    sched.add_system("post_update", CounterSystem("post1", log), order=5)

    sched.run(world, dt=0.1)

    # phases in insertion order: pre_update, update, post_update
    # within phase: sorted by 'order'
    assert log == ["pre1", "update0", "update1", "post1"]


def test_scheduler_add_function_wrapper():
    world = World()
    sched = Scheduler()

    log: list[str] = []

    def func_sys(world: World, dt: float) -> None:
        log.append(f"tick-{dt:.2f}")

    sched.add_function("update", func_sys, order=0)

    sched.run(world, 0.1)
    sched.run(world, 0.2)

    assert log == ["tick-0.10", "tick-0.20"]
