#Attempting to separate classes into separate files
import pymunk
import pygame
import pymunk.pygame_util
import random
from typing import List


class BouncyBombs(object):
    """This class creates a pymunk+pygame screen with gravity and a platform."""

    def __init__(self) -> None:
        
        self._space = pymunk.Space()
        self._space.gravity = (0.0, 900.0)

        self._fps = 1.0 / 60.0
        self._physics_per_frame = 1

        pygame.init()
        self._screen_size = (600, 600)
        self._screen = pygame.display.set_mode(self._screen_size)
        self._clock = pygame.time.Clock()

        self._draw_options = pymunk.pygame_util.DrawOptions(self._screen)

        self._add_platform()

        self._bombs: List[pymunk.Circle] = []

        self._enemies: List[pymunk.Poly] = []

        self._running = True

        self._font = pygame.font.SysFont("Arial", 16, True)

        self._collision_types = {
            "bomb" : 1,
            "enemy" : 2,
            "player" : 3
        }


    def run(self) -> None:
        while self._running:
            for time in range(self._physics_per_frame):
                self._space.step(self._fps)

            self._process_events()
            self._update_balls()
            self._clear_screen()
            self._draw_objects()
            self._show_instructions()
            pygame.display.flip()

            self._clock.tick(50)

    def _add_platform(self) -> None:
        static_body = self._space.static_body
        static_floor = pymunk.Segment(static_body, (0, self._screen_size[1]), (800, self._screen_size[1]), 10)
        #static_wall = pymunk.Segment(static_body, (100, self._screen_size[1]), (100, self._screen_size[1]-50), 5)
        static_floor.elasticity = 0.90
        static_floor.friction = 0.9

        self._space.add(static_floor)

    def _show_instructions(self) -> None:
        self._screen.blit(
            self._font.render(
                "Press space to launch a bomb",
                1,
                pygame.Color("darkgrey"),
            ),
            (5, 18),
        )
        self._screen.blit(
            self._font.render(
                "Press ESC or Q to quit", 1, pygame.Color("darkgrey")
            ),
            (5, 5)
        )

    def _process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self._running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._create_ball()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._create_enemy()


    def _update_balls(self) -> None:
        # Remove balls that exit the screen
        balls_to_remove = [ball for ball in self._bombs if 
                           ball.body.position.y < 0 
                           or ball.body.position.x > self._screen_size[0]
                           or ball.body.position.x < 0]
        for ball in balls_to_remove:
            self._space.remove(ball, ball.body)
            self._bombs.remove(ball)

    def _create_ball(self) -> None:
        mass = 10
        radius = 10
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        body = pymunk.Body(mass, inertia)
        body.position = 50, self._screen_size[1]-50
        shape = pymunk.Circle(body, radius, (0, 0))
        shape.group = 1
        shape.elasticity = 0.8
        shape.friction = 0.9
        shape.color = pygame.Color((100, 100, 100))
        shape.collision_type = self._collision_types["bomb"]
        self._space.add(body, shape)
        body.velocity = pymunk.Vec2d(100, -900) 
        def _launch_velocity(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, (0, 900.0), damping, dt)
        body.velocity_func = _launch_velocity
        self._bombs.append(shape)

    def _create_enemy(self) -> None:
        mass = 10
        inertia = pymunk.moment_for_box(mass, (10, 10))
        body = pymunk.Body(mass, inertia)
        body.position = self._screen_size[0] + 20, self._screen_size[1] - 20
        shape = pymunk.Poly.create_box(body, (30, 30))
        shape.color = pygame.Color((255, 0, 0))
        shape.group = 2
        shape.elasticity = 0.9
        shape.collision_type = self._collision_types["enemy"]
        body.velocity = pymunk.Vec2d(-70, 0)
        def _constant_velocity(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, (0, 900), damping, dt)
        body.velocity_func = _constant_velocity

        self._enemies.append(shape)
        self._space.add(body, shape)

    def _clear_screen(self) -> None:
        self._screen.fill(pygame.Color("white"))

    def _draw_objects(self) -> None:
        self._space.debug_draw(self._draw_options)



def main():
    game = BouncyBombs()
    game.run()


if __name__ == "__main__":
    main()