# Mario
# Date: 01 / jan / 1999
# Author: Edgar A. M.

"""
This is the last version and it includes many stages, each stage simply speeds 
up the game whenever you reach certain amount of points. The number of stages
is subjective as well as the speed increment in each stage.
"""

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
        # keep Mario on the ground while running, gravity is trying
        # to pull him down!
        self.rect.top = MARIO_TOP
        
        # increase frame rate slowly:
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
                self.crash.play()
                GAME_ON = False
                self.jumping = False
                self.image = self.dead
                
    def update(self, _pipes):
        self.check_collision(_pipes)

        if GAME_ON:
            # pull Mario down
            self.swoosh()
        
            if self.jumping:
                # if jumping and going down:
                if self.amount > 0:
                    # has Mario's head reached its original position?
                    if self.rect.top >= MARIO_TOP:
                        # if it hits the ground and bounce=True
                        # (it will jump again right after this)
                        if self.bounce:
                            # jump sounds
                            self.jump.play()
                            # jumping state is set to True
                            self.jumping = True
                            # change the image
                            self.image = self.airborne
                            # stop vertical amount of movement
                            self.amount = 0
                            # jump again!
                            self.amount -= self.hop
                        # if it hits the ground and bounce=False
                        # (it will run right after this)
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

    # object count
    count = 0
    
    def __init__(self):
        super().__init__()

        # even objects created choose from the four different pipes
        if not Pipe.count % 2:
            self.image = pipe_images[ random.choice((0, 1, 2, 3)) ]
        # odd objects created choose from all pipes but the big cluster
        else:
            self.image = pipe_images[ random.choice((0, 1, 2, 0)) ]
        self.rect = self.image.get_rect(midbottom=(WIDTH, FLOOR_TOP))

        # increase count of objects created as soon as a pipe is created
        Pipe.count += 1

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

        # this statement is only executed once right after game over,
        # the switch makes sure that this happens only once, that is,
        # the last score is appended to the highest scores list.
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
pygame.mixer.pre_init(44100, -16, 2, 512)       # sounds settings
pygame.init()                                   # init module
pygame.mouse.set_visible(False)                 # no mouse cursor
clock = pygame.time.Clock()                     # create clock
SPAWNPIPE = pygame.USEREVENT                    # pipe event
PIPE_FREQ = 700                                 # 700 is 0.7 seconds
pygame.time.set_timer(SPAWNPIPE, PIPE_FREQ)     # timer for pipe event
SPAWNPOINT = pygame.USEREVENT + 1               # score event
SCORE_FREQ = 100                                # 100 is 0.1 seconds
pygame.time.set_timer(SPAWNPOINT, SCORE_FREQ)   # timer for score event

""" Game variables """
WIDTH, HEIGHT = 1024, 512           # screen dimensions
INIT_SPEED = 9                      # initial stage speed
SPEED = INIT_SPEED                  # later stages speed
FLOOR_TOP = HEIGHT - 64             # vertical position of the floor top
MARIO_TOP = FLOOR_TOP - 32          # vertical position of Mario's head
DAMPENING = 0.25                    # sprite refreshment dampening factor
GAME_ON = True                      # game over status

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
            # 50% probability of pipe creation
            if random.choice((1, 0)):
                pipes.add(Pipe())
                
        if event.type == SPAWNPOINT and GAME_ON:
            # Increase score
            score.increase()
            # Increase difficulty every certain points (values are subjective),
            # the more "if" statements, the more stages of difficulty levels.
            if score.current == 100:
                SPEED += 1
            if score.current == 500:
                SPEED += 1
            if score.current == 1000:
                SPEED += 1
            
        if event.type == pygame.KEYDOWN:

            # escape key to kill the game and the window
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # Mario is running, you've just pressed the space bar!
            if event.key == pygame.K_SPACE and mario.sprite.jumping == False:
                # 1: jump sound
                # 2: jumping state is true
                # 3: bounce option is true
                # 4: change image
                # 5: set vertical amount of movement to zero
                # 6: move Mario upwards
                mario.sprite.jump.play()                    # 1
                mario.sprite.jumping = True                 # 2
                mario.sprite.bounce = True                  # 3
                mario.sprite.image = mario.sprite.airborne  # 4
                mario.sprite.amount = 0                     # 5
                mario.sprite.amount -= mario.sprite.hop     # 6

            # You died! You want to play again and press the space bar!
            if event.key == pygame.K_SPACE and not GAME_ON:
                # 1: Game on again to move floor and pipes
                # 2: score appender switch
                # 3: reset speed to the original speed value
                GAME_ON = True                              # 1
                score.switch = True                         # 2
                SPEED = INIT_SPEED                          # 3

        # You've just jumped and then you release the space bar    
        if event.type == pygame.KEYUP:
            # gravity is magnified in order to bring Mario down faster
            mario.sprite.amount += mario.sprite.factor * mario.sprite.gravity
            # deactivate the bounce option
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
    

