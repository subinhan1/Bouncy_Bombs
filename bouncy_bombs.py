import pymunk               # Import pymunk
import pygame


pygame.init()
display = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()
FPS = 50
space = pymunk.Space()      # Create a Space which contain the simulation
space.gravity = 0,981      # Set its gravity

body = pymunk.Body()        # Create a Body
body.position = 500, 500      # Set the position of the body

shape = pymunk.Circle(body, 10) # Create a circle shape and attach to body
shape.mass = 10              # Set the mass on the shape
shape.density = 1
space.add(body, shape)       # Add both body and shape to the simulation


def game():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        display.fill((255, 255, 255))
        x, y = body.position
        pygame.draw.circle(display, (255, 0, 0), (int(x), int(y)), 10)
        pygame.display.update()
        clock.tick(FPS)
        space.step(1/FPS)

game()



pygame.quit