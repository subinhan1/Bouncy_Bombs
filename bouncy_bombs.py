#Import libraries
import pymunk
import pygame


pygame.init()
window_size = (800, 800)
display = pygame.display.set_mode(window_size)
clock = pygame.time.Clock()
FPS = 50

# Create a Space which contain the simulation
space = pymunk.Space()

# Set its gravity
space.gravity = 0,981

# Create a Body
bomb = pymunk.Body()
# Set the position of the body
bomb.position = window_size[0]/2, window_size[1]/2

# Create a circle shape and attach to body
shape = pymunk.Circle(bomb, 10) 
# Set the mass and density on the shape
shape.mass = 10
shape.density = 1
# Add both body and shape to the simulation
space.add(bomb, shape)

# Create floor
floor = pymunk.Body(body_type=pymunk.Body.STATIC)
floor.shape = pymunk.Segment(floor, (0, 750), (800, 750), 50)
#floor.position = window_size[0]/2, window_size[1]
space.add(floor)


#Create game loop
def game():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        display.fill((255, 255, 255))
        x, y = bomb.position
        pygame.draw.circle(display, (255, 0, 0), (int(x), int(y)), 10)
        #pygame.draw.rect(display, (128, 128, 128), (0, window_size[0]-50, window_size[0], 100))
        pygame.display.update()
        clock.tick(FPS)
        space.step(1/FPS)

game()



pygame.quit