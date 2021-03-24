# Mario
# Date: 12 / mar / 2021
# Author: Edgar A. M.

import pygame
import sys
import random

""" Preload pipe images """
pipe_images = []
pipe_images.append(pygame.image.load("pipe_small.png"))
pipe_images.append(pygame.image.load("pipe_twins.png"))
pipe_images.append(pygame.image.load("pipe_big.png"))
pipe_images.append(pygame.image.load("pipe_cluster.png"))

""" Mario object """
class Mario(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # sounds
        self.jump = pygame.mixer.Sound('jump.wav')
        self.crash = pygame.mixer.Sound('crash.wav')
        
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
        self.gravity = 0.60

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
                self.crash.play()
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
                            self.jump.play()
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

    # object count
    count = 0
    
    def __init__(self):
        super().__init__()

        if not Pipe.count % 2:
            self.image = pipe_images[ random.choice((0, 1, 2, 3)) ]
        else:
            self.image = pipe_images[ random.choice((0, 1, 2, 0)) ]
        self.rect = self.image.get_rect(midbottom=(WIDTH, FLOOR_TOP))
        Pipe.count += 1

    def destroy(self):
        if self.rect.right <= 0:
            self.kill()

    def update(self):
        if GAME_ON:
            self.rect.x -= SPEED
        else:
            self.kill()
        self.destroy()

""" Score """
class Score():
    def __init__(self):
        self.high = [0]
        self.current = 0
        self.font = pygame.font.SysFont('FiraCode', 32)
        self.switch = True

    def increase(self):
        self.current += 1

    def update(self):
        color = (255, 255, 255)

        if GAME_ON == False and self.switch == True:
            self.high.append(self.current)
            self.current = 0
            self.switch = False
            
        # highest score
        text = 'HI ' + str(max(self.high)).zfill(5)
        pos = (700, 24)     
        screen.blit(self.font.render(text, True, color), pos)

        # current score
        text = str(self.current).zfill(5)
        pos = (900, 24)     
        screen.blit(self.font.render(text, True, color), pos)

""" Settings """
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
SPAWNPIPE = pygame.USEREVENT
PIPE_FREQ = 700
pygame.time.set_timer(SPAWNPIPE, PIPE_FREQ)
SPAWNPOINT = pygame.USEREVENT + 1
SCORE_FREQ = 100
pygame.time.set_timer(SPAWNPOINT, SCORE_FREQ)

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
score = Score()
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
        if event.type == SPAWNPOINT and GAME_ON:
            score.increase()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE and mario.sprite.jumping == False:
                mario.sprite.jump.play()
                mario.sprite.jumping = True
                mario.sprite.bounce = True
                mario.sprite.image = mario.sprite.airborne
                mario.sprite.amount = 0
                mario.sprite.amount -= mario.sprite.hop
            if event.key == pygame.K_SPACE and not GAME_ON:
                GAME_ON = True
                score.switch = True
        if event.type == pygame.KEYUP:
            mario.sprite.amount += mario.sprite.factor * mario.sprite.gravity
            mario.sprite.bounce = False
             
    # Drawing
    background.update()
    floor.update()
    score.update()
    pipes.draw(screen)
    pipes.update()
    mario.draw(screen)
    mario.update(pipes)
    pygame.display.flip()
    clock.tick(120)
    
