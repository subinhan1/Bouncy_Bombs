import pymunk
import pygame
import pymunk.pygame_util
import random
from typing import List


class BouncyBombs(object):
    """This class creates a pymunk+pygame bouncing bomb game."""

    def __init__(self) -> None:
        
        self._space = pymunk.Space()
        self._space.gravity = (0.0, 900.0)

        self._fps = 1.0 / 60.0
        self._physics_per_frame = 1

        pygame.init()
        self._screen_size = (600, 600)
        self._screen = pygame.display.set_mode(self._screen_size)
        self._screen_title = pygame.display.set_caption("Bouncy Bombs")
        self._clock = pygame.time.Clock()

        self._draw_options = pymunk.pygame_util.DrawOptions(self._screen)
        
        self._HP = 100

        self._bombs: List[pymunk.Circle] = []

        self._enemies: List[pymunk.Poly] = []

        self._ticks_to_next_enemy = 5

        self._running = True

        self._font1 = pygame.font.SysFont("Arial", 14, True)
        self._font2 = pygame.font.SysFont("Arial", 26, True)

        #Objects with the same collision type do not collide with each other
        self._collision_types = {
            "bomb" : 1,
            "player" : 2,
            "enemy" : 3
        }

        self._add_platform()

    #Main game loop
    def run(self) -> None:
        while self._running:
            for time in range(self._physics_per_frame):
                self._space.step(self._fps)

            self._process_events()
            self._add_player()
            self._update_balls()
            self._sense_damage()
            self._clear_screen()
            self._draw_objects()
            self._show_instructions()
            self._show_HP()
            self._update_ground_enemy()
            self._update_air_enemy()
            self._show_end_screen()
            pygame.display.flip()

            self._clock.tick(50)

    #Add ground platform and set elasticity (how bouncy it is)
    def _add_platform(self) -> None:
        static_body = self._space.static_body
        static_floor = pymunk.Segment(static_body, (0, self._screen_size[1]), (800, self._screen_size[1]), 10)
        static_wall = pymunk.Segment(static_body, (-50, 0), (-50, self._screen_size[1]), 5)
        static_wall.collision_type = self._collision_types["player"]
        static_wall.elasticity = 1
        static_floor.elasticity = 0.90
        static_floor.friction = 0.9

        self._space.add(static_floor, static_wall)

    #Add main player that cannot be hit
    def _add_player(self) -> None:
        static_body = self._space.static_body
        static_body.position = 35, self._screen_size[1]-25
        static_player = pymunk.Poly.create_box(static_body, (30, 30))
        static_player.color = pygame.Color("blue")
        static_player.collision_type = self._collision_types["player"]
        static_player.elasticity = 1.0
        self._space.add(static_player)

    #Print basic controls on top left of screen in grey
    def _show_instructions(self) -> None:
        self._screen.blit(
            self._font1.render(
                "ARROW UP = High Bomb    |   ARROW DOWN = Low Bomb",
                1,
                pygame.Color("darkgrey"),
            ),
            (5, 18),
        )
        self._screen.blit(
            self._font1.render(
                "Press ESC or Q to quit", 1, pygame.Color("darkgrey")
            ),
            (5, 2)
        )

    #Print HP on top right of screen in red
    def _show_HP(self) -> None:
        self._screen.blit(
            self._font2.render(
                "HP: " + str(self._HP),
                1,
                pygame.Color("red")
            ),
            (self._screen_size[0]-100, 2)
        )

    def _show_end_screen(self) -> None:
        if self._HP <= 0:
            self._screen.fill(pygame.Color("black"))
            self._screen.blit(
                self._font2.render(
                    "GAME OVER",
                    1,
                    pygame.Color("white")
                ),
            (self._screen_size[0]/2 - 80, self._screen_size[1]/2 - 15)
        )



    #Sense collisions, reduce HP and erase enemy
    def _sense_damage(self) -> None:
        """If enemy gets over the x<0 or collides with player, deplete HP and remove enemies"""
        h_0 = self._space.add_collision_handler(self._collision_types["player"], self._collision_types["enemy"])
        def remove_enemy(arbiter, space, data):
            enemy_shape = arbiter.shapes[1]
            self._space.remove(enemy_shape, enemy_shape.body)
            return True
        h_0.begin = self._damaged
        h_0.separate = remove_enemy

        h_1 = self._space.add_collision_handler(self._collision_types["bomb"], self._collision_types["enemy"])
        def remove_bomb_and_enemy(arbiter, space, data):
            bomb_shape = arbiter.shapes[0]
            enemy_shape = arbiter.shapes[1]
            self._space.remove(bomb_shape, bomb_shape.body, enemy_shape, enemy_shape.body)
            return True
        h_1.begin = remove_bomb_and_enemy


    def _damaged(self, arbiter, space, data):
        self._HP -= 20
        return True
    
    #Process key presses/user input
    def _process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self._running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self._create_high_bomb()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self._create_low_bomb()

    
    def _update_balls(self) -> None:
        # Remove balls that exit the screen
        balls_to_remove = [ball for ball in self._bombs if 
                           ball.body.position.y < 0 
                           or ball.body.position.x > self._screen_size[0]
                           or ball.body.position.x < 0
                        ]
        for ball in balls_to_remove:
            self._space.remove(ball, ball.body)
            self._bombs.remove(ball)

    #Create a bomb that launches with a high projectory
    def _create_high_bomb(self) -> None:
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
        body.velocity = pymunk.Vec2d(200, -900) 
        def _launch_velocity(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, (0, 900.0), damping, dt)
        body.velocity_func = _launch_velocity
        self._bombs.append(shape)

    #Create a bomb that launches with a low projectory
    def _create_low_bomb(self) -> None:
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
        body.velocity = pymunk.Vec2d(250, -400) 
        def _launch_velocity(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, (0, 900.0), damping, dt)
        body.velocity_func = _launch_velocity
        self._bombs.append(shape)

    #Spawn a grounded box enemy with a medium speed
    def _create_ground_enemy(self) -> None:
        mass = 10
        inertia = pymunk.moment_for_box(mass, (10, 10))
        body = pymunk.Body(mass, inertia)
        body.position = self._screen_size[0] + 20, self._screen_size[1] - 20
        shape = pymunk.Poly.create_box(body, (30, 30))
        shape.color = pygame.Color((255, 0, 0))
        shape.group = 2
        shape.elasticity = 0.9
        shape.collision_type = self._collision_types["enemy"]
        body.velocity = pymunk.Vec2d(-50, 0)

        #After a certain time, speed up enemies to increase difficulty
        if pygame.time.get_ticks() > 25000:
            body.velocity = pymunk.Vec2d(-100, 0)
        def _constant_velocity(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, (0, 900), damping, dt)
        body.velocity_func = _constant_velocity
        self._enemies.append(shape)
        self._space.add(body, shape)

    #Spawn an airborne enemy with a high speed
    def _create_air_enemy(self) -> None:
        mass = 10
        inertia = pymunk.moment_for_box(mass, (10, 10))
        body = pymunk.Body(mass, inertia)
        body.position = self._screen_size[0] + 20, self._screen_size[1]/3
        shape = pymunk.Poly.create_box(body, (40, 10))
        shape.color = pygame.Color((255, 0, 0))
        shape.group = 2
        shape.elasticity = 0.9
        shape.collision_type = self._collision_types["enemy"]
        body.velocity = pymunk.Vec2d(-100, 0)

        #After a certain time, speed up enemies to increase difficulty
        if pygame.time.get_ticks() > 25000:
            body.velocity = pymunk.Vec2d(-200, 0)
        def _constant_velocity(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, (0, 0), damping, dt)
        body.velocity_func = _constant_velocity
        self._enemies.append(shape)
        self._space.add(body, shape)

    #Create random time intervals for grounded enemies
    def _update_ground_enemy(self) -> None:
        self._ticks_to_next_enemy -= 1
        if self._ticks_to_next_enemy <= 0:
            self._create_ground_enemy()
            self._ticks_to_next_enemy = random.randint(100, 200)
    
    #Create random time intervals for airborne enemies
    def _update_air_enemy(self) -> None:
        self._ticks_to_next_enemy -= 1
        if self._ticks_to_next_enemy <= 0:
            self._create_air_enemy()
            self._ticks_to_next_enemy = random.randint(250, 400)

        

    #Clear screen
    def _clear_screen(self) -> None:
        self._screen.fill(pygame.Color("white"))

    #Draw objects on screen (all objects are not visible until drawn by this function)
    def _draw_objects(self) -> None:
        self._space.debug_draw(self._draw_options)



#Creates an instance of the game class and runs the game
def main():
    game = BouncyBombs()
    game.run()


if __name__ == "__main__":
    main()