#!/usr/bin/env python3.9
import sys
from math import sqrt

import pygame
from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_ESCAPE,
    K_SPACE,
    K_UP,
    K_RIGHT,
    K_LEFT,
)

pygame.init()
pygame.font.init()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        img = pygame.image.load("images/player.png")
        img = pygame.transform.scale(img, (34, 34))
        self.image = img
        self.surf = pygame.Surface((34, 34))
        self.surf.fill('white')
        self.rect = self.image.get_rect()
        self.rect.center = (250, 250)

        self.velocity = [0, 0]

        self.speed = 5
        self.acceleration = 0.2
        # self.can_jump = True

    def do_gravity(self):
        self.velocity[1] += 1

    def can_jump(self, walls):
        class Temp(pygame.sprite.Sprite):
            def __init__(self, player_rect):
                super(Temp, self).__init__()
                self.rect = pygame.Rect(player_rect.left, player_rect.bottom + 2, player_rect.width, 1)

        temp = Temp(self.rect)

        if len(pygame.sprite.spritecollide(temp, walls, False)) == 0:
            return False
        else:
            return True

    def is_dead(self):
        if self.rect.top > 500:
            return True
        return False

    def get_velocity(self):
        return round(sqrt(pow(self.velocity[0], 2) + pow(self.velocity[1], 2)))

    def update(self, pressed, player_group, walls):

        self.do_gravity()

        if pressed[K_UP] and self.can_jump(walls):
            self.velocity[1] = -15
        if pressed[K_RIGHT]:
            self.velocity[0] += self.acceleration
        # if pressed[K_DOWN]:
        #     self.velocity[1] += self.acceleration
        if pressed[K_LEFT]:
            self.velocity[0] += -self.acceleration
        # if not pressed[K_RIGHT] and not pressed[K_LEFT] and not pressed[K_UP] and not pressed[K_DOWN]:
        self.velocity[0] = self.velocity[0] * 0.98
        # self.velocity[1] = self.velocity[1] * 0.96

        self.rect.move_ip(self.velocity[0], 0)

        for wall in pygame.sprite.spritecollide(self, walls, False):
            if self.velocity[0] < 0:
                self.rect.left = wall.rect.right

            if self.velocity[0] > 0:
                self.rect.right = wall.rect.left

            self.velocity = [0, self.velocity[1]]

        self.rect.move_ip(0, self.velocity[1])

        for wall in pygame.sprite.spritecollide(self, walls, False):
            if self.velocity[1] < 0:
                self.rect.top = wall.rect.bottom

            if self.velocity[1] > 0:
                self.rect.bottom = wall.rect.top

            self.velocity = [self.velocity[0], 0]

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Block(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2, colour):
        super(Block, self).__init__()
        self.x1, self.x2, self.y1, self.y2 = x1, x2, y1, y2
        self.surf = pygame.Surface((x2 - x1, y2 - y1))
        self.surf.fill(colour)
        self.rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)

    def draw(self, surface):
        surface.blit(self.surf, self.rect)


class Room(pygame.sprite.Sprite):
    def __init__(self, background, walls, spawn_point=(250, 250), exit_=None):
        super(Room, self).__init__()
        if exit_ is None:
            exit_ = [(Block(0, 0, 1, 1, 'gold'), 'room1', (250, 250))]
        self.background = background
        self.walls = walls
        self.spawn_point = spawn_point
        self.exit_ = exit_

    def draw(self, surface):
        for i in self.walls:
            i.draw(surface)
        for i in self.exit_:
            i[0].draw(surface)

    def get_block_group(self, group):
        for i in self.walls:
            group.add(i)
        return group

    def get_exit_group(self, group):
        print(self.exit_)
        for i in self.exit_:
            group.add(i[0])
        return group

    def respawn(self, player_):
        player_.rect.center = self.spawn_point

    def get_door(self):
        for i in self.exit_:
            if pygame.sprite.collide_rect(player, i[0]):
                return i


def load_room(current_, room_dict_):
    next_room = current_['current room'].get_door()
    player.rect.center = next_room[2]
    current_['current room'] = room_dict_[next_room[1]]
    current_['blocks'] = current_['current room'].get_block_group(pygame.sprite.Group())
    current_['exits'] = current_['current room'].get_exit_group(pygame.sprite.Group())
    # current_['current room'].set_to_start(player)
    player.velocity = [0, 0]
    return current_


room2 = Room(None,
             [Block(50, 450, 450, 475, '#ff00ff'),
              Block(77, 359, 178, 385, '#ff00ff'),
              Block(268, 298, 380, 330, '#ff00ff'),
              Block(57, 197, 159, 248, '#ff00ff'),
              Block(316, 380, 344, 454, '#ff00ff'),
              Block(272, 153, 393, 177, '#ff00ff'),
              Block(91, 69, 172, 99, '#ff00ff')],
             spawn_point=(250, 427),
             exit_=[(Block(114, 22, 146, 69, 'gold'), 'room3', (106, 307))])


room1 = Room(None,
             [Block(50, 449, 448, 472, 'cyan'),
              Block(204, 380, 276, 402, 'cyan'),
              Block(322, 342, 384, 360, 'cyan'),
              (Block(53, 79, 131, 105, 'cyan')),
              Block(229, 77, 271, 96, 'cyan'),
              Block(384, 76, 429, 84, 'cyan'),
              Block(506, 288, 585, 325, 'cyan'),
              Block(624, 198, 690, 231, 'cyan'),
              Block(523, 113, 571, 148, 'cyan')],
             spawn_point=(139, 421),
             exit_=[(Block(335, 281, 366, 342, 'gold'), 'room2', (250, 427)),
                    (Block(397, 25, 416, 76, 'gold'), 'secret', (250, 250))])

room3 = Room(None,
             [Block(76, 395, 134, 412, 'red'),
              Block(229, 342, 278, 360, 'red'),
              Block(338, 292, 391, 312, 'red'),
              # Block(141, 39, 146, 295, 'red'),
              Block(223, 212, 260, 226, 'red'),
              Block(120, 148, 160, 167, 'red'),
              Block(374, 60, 428, 78, 'red'),
              Block(234, 90, 272, 107, 'red')],
             exit_=[(Block(380, 14, 413, 60, 'gold'), 'room4', (80, 39))],
             spawn_point=(106, 307))


room4 = Room(None,
             [Block(45, 76, 116, 96, 'orange'),
              Block(177, 215, 252, 240, 'orange'),
              Block(330, 96, 392, 124, 'orange')],
             spawn_point=(80, 39),
             exit_=[(Block(196, 176, 227, 215, 'gold'), 'room5', (130, 378)),
                    (Block(348, 43, 369, 96, 'gold'), 'room1', (87, 41))])

room5 = Room(None,
             [Block(79, 413, 155, 453, 'light green'),
              Block(189, 346, 242, 374, 'light green'),
              Block(281, 283, 352, 308, 'light green'),
              Block(134, 216, 214, 239, 'light green'),
              Block(40, 147, 85, 169, 'light green'),
              Block(193, 92, 256, 117, 'light green'),
              Block(337, 95, 384, 111, 'light green'),
              Block(400, 33, 416, 454, 'light green'),
              Block(400, 433, 488, 454, 'light green')],
             exit_=[(Block(438, 378, 463, 433, 'gold'), 'win_1', (250, 250))])

secret_room = Room(None, [Block(141, 295, 339, 354, 'yellow')])

win_1 = Room(None, [Block(0, 0, 1, 1, 'black')])


room_dict = {'room1': room1,
             'room2': room2,
             'room3': room3,
             'room4': room4,
             'room5': room5,
             'secret': secret_room,
             'win_1': win_1}


current_room = room1


# surface
surf = pygame.display.set_mode((500, 500))
pygame.display.set_caption("move returns")
pygame.display.set_icon(pygame.image.load("images/player.png"))


# colours
BLACK = pygame.Color(0, 0, 0)

BACKGROUND = pygame.Color(0, 51, 102)


# fps
FPS = 60
fps = pygame.time.Clock()

# groups
players = pygame.sprite.Group()
blocks = current_room.get_block_group(pygame.sprite.Group())
exits = current_room.get_exit_group(pygame.sprite.Group())
current = {'current room': current_room,
           'blocks': current_room.get_block_group(pygame.sprite.Group()),
           'exits': current_room.get_exit_group(pygame.sprite.Group())}

# player
player = Player()
players.add(player)
current_room.respawn(player)

# font set up
vel_font = pygame.font.SysFont('arial', 30)


running = True
while running:

    ##################################
    #             event              #
    ##################################

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_SPACE:
                if len(pygame.sprite.groupcollide(players, current['exits'], False, False)):
                    current = load_room(current, room_dict)
                if current['current room'] == win_1:
                    won = True
                    while won:
                        for event_ in pygame.event.get():
                            if event_.type == QUIT:
                                won = False
                                pygame.quit()
                                sys.exit()
                            if event_.type == KEYDOWN:
                                if event_.key == K_ESCAPE:
                                    won = False
                                    pygame.quit()
                                    sys.exit()

                        surf.fill(BACKGROUND)

                        msg = pygame.font.SysFont('arial', 30).render("well done", False, (255, 255, 255))
                        rect = msg.get_rect()
                        rect.center = (250, 156)
                        surf.blit(msg, rect)
                        msg = pygame.font.SysFont('arial', 30).render("you completed the game", False, (255, 255, 255))
                        rect = msg.get_rect()
                        rect.center = (250, 208)
                        surf.blit(msg, rect)

                        pygame.display.update()
                if current['current room'] == secret_room:
                    won = True
                    while won:
                        for event_ in pygame.event.get():
                            if event_.type == QUIT:
                                won = False
                                pygame.quit()
                                sys.exit()
                            if event_.type == KEYDOWN:
                                if event_.key == K_ESCAPE:
                                    won = False
                                    pygame.quit()
                                    sys.exit()

                        surf.fill(BACKGROUND)

                        msg = pygame.font.SysFont('arial', 30).render("well done", False, (255, 255, 255))
                        rect = msg.get_rect()
                        rect.center = (250, 156)
                        surf.blit(msg, rect)
                        msg = pygame.font.SysFont('arial', 30).render("you found the secret ending", False, (255, 255, 255))
                        rect = msg.get_rect()
                        rect.center = (250, 208)
                        surf.blit(msg, rect)

                        pygame.display.update()

    ##################################
    #             update             #
    ##################################

    pressed_keys = pygame.key.get_pressed()

    player.update(pressed_keys, players, current['blocks'])

    if player.is_dead():
        current['current room'].respawn(player)
        player.velocity = [0, 0]

    vel_text = vel_font.render(f"{player.get_velocity()}", False, (0, 0, 0))

    ##################################
    #             render             #
    ##################################

    surf.fill(BACKGROUND)

    # pygame.draw.circle(surf, 'pink', (250, 250), 200, 2)

    current['current room'].draw(surf)

    player.draw(surf)

    # surf.blit(vel_text, (0, 0))

    pygame.display.update()

    fps.tick(FPS)
