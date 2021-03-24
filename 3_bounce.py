# Mario
# Date: 12 / mar / 2021
# Author: Edgar A. M.

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

        # bounce opportunity
        self.bounce = True

        # hop increment
        self.hop = 10

        # vertical movement amount
        self.amount = 0

        # gravity
        self.gravity = 0.6

        # gravity factor
        self.factor = 5

    def run(self):
        # keep Mario on the ground
        self.rect.top = MARIO_TOP
        
        # increase slowly:
        self.frame += DAMPENING
        
        if self.frame >= len(self.sprites):
            self.frame = int(0)
            self.image = self.sprites[self.frame]
        else:
            self.image = self.sprites[ int(self.frame) ]

    def swoosh(self):
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

            self.swoosh()
        
            if self.jumping:
                if self.amount > 0:
                    if self.rect.top >= MARIO_TOP:
                        if self.bounce:
                            self.jumping = True
                            self.image = self.airborne
                            self.amount = 0
                            self.amount -= self.hop
                        else:
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
        self.xloc -= SPEED
        if self.xloc <= -WIDTH:
            self.xloc = 0

    def draw(self):
        screen.blit(self.image, (self.xloc, FLOOR_TOP))
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
        screen.blit(self.image, (0, 0))

""" Pipe object """
class Pipe(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pipe_images[ random.choice((0, 1, 2, 3)) ]
        self.rect = self.image.get_rect(midbottom=(WIDTH, FLOOR_TOP))

    def destroy(self):
        if self.rect.right <= 0:
            self.kill()

    def update(self):
        if GAME_ON:
            self.rect.x -= SPEED
        else:
            self.kill()
        self.destroy()

""" Settings """
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
SPAWNPIPE = pygame.USEREVENT
PIPE_FREQ = 700
pygame.time.set_timer(SPAWNPIPE, PIPE_FREQ)

""" Game variables """
WIDTH, HEIGHT = 1024, 512
SPEED = 8
FLOOR_TOP = HEIGHT - 64
MARIO_TOP = FLOOR_TOP - 32
DAMPENING = 0.25
GAME_ON = True

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
            if random.choice((1, 0)):
                pipes.add(Pipe())
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE and mario.sprite.jumping == False:
                mario.sprite.jumping = True
                mario.sprite.bounce = True
                mario.sprite.image = mario.sprite.airborne
                mario.sprite.amount = 0
                mario.sprite.amount -= mario.sprite.hop
            if event.key == pygame.K_SPACE and not GAME_ON:
                GAME_ON = True
        if event.type == pygame.KEYUP:
            mario.sprite.amount += mario.sprite.factor * mario.sprite.gravity
            mario.sprite.bounce = False
             
    # Drawing
    background.update()
    floor.update()
    pipes.draw(screen)
    pipes.update()
    mario.draw(screen)
    mario.update(pipes)
    pygame.display.flip()
    clock.tick(60)
    
