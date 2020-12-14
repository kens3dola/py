import pygame as pg
from Multimedia.demo.settings import *


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.color = RED
        self.L, self.R, self.U, self.D = False, False, False, False
        self.y_vel = 1
        self.movement = [0, 0]
        self.imgs = [pg.image.load('i/big_demon_idle_anim_f0.png'),
                     pg.image.load('i/big_demon_idle_anim_f1.png'),
                     pg.image.load('i/big_demon_idle_anim_f2.png'),
                     pg.image.load('i/big_demon_idle_anim_f3.png')]
        self.frame = 0
        self.last_time = pg.time.get_ticks()
        self.g = 1

    def update(self):
        if self.y_vel < 7:
            self.y_vel += 1
        self.movement = [0, 0]
        if self.L:
            self.movement[0] = -5
        if self.R:
            self.movement[0] = 5
        if self.U:
            self.g -= 2
        # if self.D:
        #     self.movement[1] = 5
        # self.movement[1] = self.y_vel
        if self.g <5:
            self.g += 0.2
        self.movement[1] = self.g

        self.movement = self.check_collision(self.movement)
        self.rect.x += self.movement[0]
        self.rect.y += self.movement[1]

        # animation
        # if pg.time.get_ticks() - self.last_time > 150:
        #     self.frame += 1
        #     self.frame = self.frame % len(self.imgs)
        #     self.last_time = pg.time.get_ticks()
        # self.image = self.imgs[self.frame]

    def check_collision(self, movement):
        rect = self.rect.copy()
        rect.x += movement[0]
        for wall in self.game.walls:
            if rect.colliderect(wall.rect):
                rect.x -= movement[0]
                if (rect.x + TILESIZE) <= wall.rect.x:
                    movement[0] = wall.rect.x - rect.x - TILESIZE
                else:
                    movement[0] = -(rect.x - wall.rect.x - TILESIZE)
        rect.y += movement[1]
        for wall in self.game.walls:
            if rect.colliderect(wall.rect):
                rect.y -= movement[1]
                if (rect.y + TILESIZE) <= wall.rect.y:
                    movement[1] = wall.rect.y - rect.y - TILESIZE
                else:
                    movement[1] = -(rect.y - wall.rect.y - TILESIZE)
        return movement


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.color = GREEN

    def update(self):
        self.rect.x += self.game.offset[0]
        self.rect.y += self.game.offset[1]
