import random
from dataclasses import dataclass

import pygame

from lazyecs import World, Scheduler


# -------------------------
# ECS Components
# -------------------------

@dataclass
class Position:
    x: float
    y: float


@dataclass
class Velocity:
    vx: float
    vy: float


@dataclass
class Circle:
    radius: float = 12.0


@dataclass
class Color:
    r: int
    g: int
    b: int


# -------------------------
# ECS Systems
# -------------------------

class InputSystem:
    """
    Handles window events + spawning new entities via mouse clicks.

    - ESC or window close -> quits
    - Left mouse button -> spawn a new bouncing circle at cursor position
    """

    def __init__(self, running_flag: list[bool], screen_size: tuple[int, int]) -> None:
        self.running_flag = running_flag
        self.screen_w, self.screen_h = screen_size

    def run(self, world: World, dt: float) -> None:  # dt unused, but keeps interface consistent
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running_flag[0] = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running_flag[0] = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                spawn_bouncy_entity(world, mx, my, self.screen_w, self.screen_h)


class MovementSystem:
    """
    Applies velocity to position for all entities that have both.
    """

    def run(self, world: World, dt: float) -> None:
        for eid, (pos, vel) in world.query(Position, Velocity):
            pos.x += vel.vx * dt
            pos.y += vel.vy * dt


class BounceSystem:
    """
    Keeps entities inside the screen bounds by bouncing them off the edges.
    """

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def run(self, world: World, dt: float) -> None:  # dt not needed here
        for eid, (pos, vel, shape) in world.query(Position, Velocity, Circle):
            r = shape.radius

            # Left / right
            if pos.x - r < 0:
                pos.x = r
                vel.vx *= -1
            elif pos.x + r > self.width:
                pos.x = self.width - r
                vel.vx *= -1

            # Top / bottom
            if pos.y - r < 0:
                pos.y = r
                vel.vy *= -1
            elif pos.y + r > self.height:
                pos.y = self.height - r
                vel.vy *= -1


class RenderSystem:
    """
    Draws all entities with Position + Circle + Color as filled circles.
    """

    def __init__(self, screen: pygame.Surface, background=(15, 15, 20)) -> None:
        self.screen = screen
        self.background = background

    def run(self, world: World, dt: float) -> None:
        self.screen.fill(self.background)

        for eid, (pos, circle, color) in world.query(Position, Circle, Color):
            pygame.draw.circle(
                self.screen,
                (color.r, color.g, color.b),
                (int(pos.x), int(pos.y)),
                int(circle.radius),
            )

        # Optional: simple FPS counter
        # (dt may vary a little per frame, but it's fine for a rough readout)
        fps_font = pygame.font.SysFont("consolas", 18)
        fps = 1.0 / dt if dt > 0 else 0.0
        fps_text = fps_font.render(f"FPS: {fps:5.1f}", True, (200, 200, 200))
        self.screen.blit(fps_text, (10, 10))

        pygame.display.flip()


# -------------------------
# Helper: spawn entities
# -------------------------

def random_color() -> tuple[int, int, int]:
    return (
        random.randint(50, 255),
        random.randint(50, 255),
        random.randint(50, 255),
    )


def spawn_bouncy_entity(world: World, x: float, y: float, width: int, height: int) -> None:
    """
    Spawn a new entity with Position, Velocity, Circle and Color.
    """
    speed = random.uniform(80, 220)
    angle = random.uniform(0, 3.14159 * 2.0)

    vx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
    vy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y

    r = random.uniform(8, 20)

    e = world.create()
    world.add(
        e,
        Position(x, y),
        Velocity(vx, vy),
        Circle(radius=r),
        Color(*random_color()),
    )


def spawn_initial_entities(world: World, width: int, height: int, count: int = 20) -> None:
    for _ in range(count):
        x = random.uniform(50, width - 50)
        y = random.uniform(50, height - 50)
        spawn_bouncy_entity(world, x, y, width, height)


# -------------------------
# Main entry point
# -------------------------

def main():
    pygame.init()
    pygame.display.set_caption("LazyECS Demo - Bouncing Circles")

    width, height = 960, 540
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    world = World()
    scheduler = Scheduler()

    running = [True]  # mutable container so systems can toggle this

    # Register systems in desired phase order:
    # 1) pre_update: handle input & spawning
    # 2) update: movement & bounce
    # 3) render: draw everything
    scheduler.add_system("pre_update", InputSystem(running, (width, height)), order=0)
    scheduler.add_system("update", MovementSystem(), order=0)
    scheduler.add_system("update", BounceSystem(width, height), order=10)
    scheduler.add_system("render", RenderSystem(screen), order=0)

    # Spawn some initial entities
    spawn_initial_entities(world, width, height, count=25)

    # Main loop
    while running[0]:
        dt_ms = clock.tick(60)
        dt = dt_ms / 1000.0

        scheduler.run(world, dt)

    pygame.quit()


if __name__ == "__main__":
    main()
