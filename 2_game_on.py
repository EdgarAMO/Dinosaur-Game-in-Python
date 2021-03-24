# Mario
# Date: 12 / mar / 2021
# Author: Edgar A. M.

"""
The game over option is available now. When you die, pipes stop moving and
they disappear, the floor stops moving and Mario freezes. To play again just
press the space bar again.
"""

import pygame
import sys
import random

""" Preload pipe images """
pipe_images = []
pipe_images.append(pygame.image.load("pipe_big.png"))
pipe_images.append(pygame.image.load("pipe_cluster.png"))
pipe_images.append(pygame.image.load("pipe_small.png"))
pipe_images.append(pygame.image.load("pipe_twins.png"))

""" Mario object """
class Mario(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # while running images
        self.sprites = []
        self.sprites.append(pygame.image.load("walk1.png"))
        self.sprites.append(pygame.image.load("walk2.png"))
        self.sprites.append(pygame.image.load("walk3.png"))

        # while jumping image
        self.airborne = pygame.image.load("walk3.png")

        # while dead image
        self.dead = pygame.image.load("dead.png")

        # initial frame
        self.frame = 0

        # current image
        self.image = self.sprites[self.frame]

        # current rect
        self.rect = self.image.get_rect(topleft=(128, MARIO_TOP))

        # jumping state
        self.jumping = False

        # hop increment
        self.hop = 10

        # vertical movement amount
        self.amount = 0

        # gravity
        self.gravity = 0.60

        # gravity factor
        self.factor = 5

    def run(self):
        # keep Mario on the ground while running, gravity is trying
        # to pull him down!
        self.rect.top = MARIO_TOP
        
        # increase slowly:
        self.frame += DAMPENING

        # if you run out of sprites, choose the first one again
        if self.frame >= len(self.sprites):
            self.frame = int(0)
            self.image = self.sprites[self.frame]
        else:
            self.image = self.sprites[ int(self.frame) ]

    def swoosh(self):
        # pull Mario down by moving the rectangle downwards
        self.amount += self.gravity
        self.rect.top += self.amount

    def check_collision(self, _pipes):
        global GAME_ON
        
        for _pipe in _pipes:
            if self.rect.colliderect(_pipe.rect):
                GAME_ON = False
                self.jumping = False
                self.image = self.dead
                
    def update(self, _pipes):
        self.check_collision(_pipes)

        if GAME_ON:
            
            # pull Mario down
            self.swoosh()
        
            if self.jumping:
                if self.amount > 0:
                    if self.rect.top >= MARIO_TOP:
                        self.jumping = False
                        self.amount = 0
                        self.rect.top = MARIO_TOP
                        self.frame = int(0)
                        self.image = self.sprites[self.frame]
            else:
                self.run()

""" Floor object """
class Floor():
    def __init__(self):
        self.image = pygame.image.load("floor.png")
        self.xloc = 0

    def move(self):
        # move to the left, add a small amount each time
        self.xloc -= SPEED
        # if the floor disappears, reset to original position
        if self.xloc <= -WIDTH:
            self.xloc = 0

    def draw(self):
        # first floor
        screen.blit(self.image, (self.xloc, FLOOR_TOP))
        # second floor that will replace the missing first floor
        screen.blit(self.image, (self.xloc + WIDTH, FLOOR_TOP))

    def update(self):
        if GAME_ON:
            self.move()
        self.draw()

""" Background object """
class Background():
    def __init__(self):
        self.image = pygame.image.load("background.png")

    def update(self):
        # (0, 0) is the upper left corner of the rectangle enclosing the image
        screen.blit(self.image, (0, 0))

""" Pipe object """
class Pipe(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pipe_images[ random.choice((0, 1, 2, 3)) ]
        self.rect = self.image.get_rect(midbottom=(WIDTH, FLOOR_TOP))

    def destroy(self):
        # pipe sprite disappears as soon as it is entirely out of the screen
        if self.rect.right <= 0:
            self.kill()

    def update(self):
        if GAME_ON:
            self.rect.x -= SPEED
        # this destroys all pipe sprites after Mario dies, otherwise
        # you will crash against the same pipe as soon as you resume
        # the game
        else:
            self.kill()
        self.destroy()

""" Settings """
pygame.mixer.pre_init(44100, -16, 2, 512)       # sounds settings
pygame.init()                                   # init module
pygame.mouse.set_visible(False)                 # no mouse cursor
clock = pygame.time.Clock()                     # create clock
SPAWNPIPE = pygame.USEREVENT                    # pipe event
PIPE_FREQ = 700                                 # 700 is 0.7 seconds
pygame.time.set_timer(SPAWNPIPE, PIPE_FREQ)     # timer for pipe event

""" Game variables """
WIDTH, HEIGHT = 1024, 512           # screen dimensions
SPEED = 9                           # later stages speed
FLOOR_TOP = HEIGHT - 64             # vertical position of the floor top
MARIO_TOP = FLOOR_TOP - 32          # vertical position of Mario's head
DAMPENING = 0.25                    # sprite refreshment dampening factor
GAME_ON = True                      # game over status

""" Objects """
screen = pygame.display.set_mode((WIDTH, HEIGHT))
background = Background()
floor = Floor()
pipes = pygame.sprite.Group()
mario = pygame.sprite.GroupSingle(Mario())

""" Main Loop """
while True:

    # Event handler
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == SPAWNPIPE and GAME_ON:
            # 50% probability of pipe creation
            if random.choice((1, 0)):
                pipes.add(Pipe())
                
        if event.type == pygame.KEYDOWN:

            # escape key to kill the game and the window
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # Mario is running, you've just pressed the space bar!
            if event.key == pygame.K_SPACE and mario.sprite.jumping == False:
                mario.sprite.jumping = True
                mario.sprite.image = mario.sprite.airborne
                mario.sprite.amount = 0
                mario.sprite.amount -= mario.sprite.hop

            # You died! You want to play again and press the space bar!  
            if event.key == pygame.K_SPACE and not GAME_ON:
                GAME_ON = True

        # You've just jumped and then you release the space bar        
        if event.type == pygame.KEYUP:
            # gravity is magnified in order to bring Mario down faster
            mario.sprite.amount += mario.sprite.factor * mario.sprite.gravity
 
    # Drawing
    background.update()
    floor.update()
    pipes.draw(screen)
    pipes.update()
    mario.draw(screen)
    mario.update(pipes)
    pygame.display.flip()
    clock.tick(60)
    
