import pygame as pg
from Multimedia.settings import *
from pygame.math import Vector2 as vec
from Multimedia.tilemap import *


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.action = 'idle'
        self.side = 'right'
        self.anim = Animation('maps/as.json', ['idle', 'walk', 'jump', 'slash'], self.action)
        self.image = pg.Surface((0, 0))
        self.anim.update(self, self.action, self.side)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.gravity = 0
        self.in_air = False
        self.air_time = 0
        self.U, self.D, self.L, self.R, self.slash = False, False, False, False, False

    def collision_rect(self):
        return pg.Rect(self.rect.x + (self.rect.width - TILE_SIZE) / 2,
                       self.rect.y + (self.rect.height - TILE_SIZE), TILE_SIZE, TILE_SIZE)

    def update(self):
        if self.in_air:
            self.air_time += 1
        movement = 0
        if self.L:
            movement = -3
        elif self.R:
            movement = 3
        if self.gravity < 10:
            self.gravity += 0.5
        movement, self.gravity = self.check_collision(movement)
        if movement == 0:
            self.action = 'idle'
        elif movement > 0:
            self.action = 'walk'
            self.side = 'right'
        elif movement < 0:
            self.action = 'walk'
            self.side = 'left'
        if self.gravity >= 1 or self.gravity < -1:
            self.in_air = True
        else:
            self.in_air = False
        if self.in_air:
            self.action = 'jump'
        if self.slash:
            self.action = 'slash'
            self.hit()
        self.rect.x += movement
        self.rect.y += self.gravity
        if self.rect.y > self.game.map.height:
            self.rect.x = 0
            self.rect.y = 0
        self.anim.update(self, self.action, self.side)

    def hit(self):
        rect = self.rect.copy().move(TILE_SIZE/2, 0)
        for mob in self.game.mobs:
            if rect.colliderect(mob.rect):
                mob.kill()

    def check_collision(self, movement):
        movement = self.collide_x(self.game.walls, movement)
        self.gravity = self.collide_y(self.game.walls, self.gravity)
        movement = self.collide_x(self.game.mobs, movement)
        self.gravity = self.collide_y(self.game.mobs, self.gravity)
        movement, self.gravity = self.collide(self.game.walls, movement, self.gravity)
        return movement, self.gravity

    def collide_x(self, tiles, movement):
        for rect in tiles:
            if self.get_collision_x(movement).colliderect(rect.rect):
                return 0
        return movement

    def collide_y(self, tiles, movement):
        for rect in tiles:
            if self.get_collision_y(movement).colliderect(rect.rect):
                self.air_time = 0
                return 0
        return movement

    def get_collision_x(self, movement):
        collision = self.collision_rect().copy()
        collision.x += movement
        return collision

    def get_collision_y(self, movement):
        collision = self.collision_rect().copy()
        collision.y += movement
        return collision

    def get_collision(self, move_x, move_y):
        collision = self.collision_rect().copy()
        collision.x += move_x
        collision.y += move_y
        return collision

    def collide(self, tiles, move_x, move_y):
        for rect in tiles:
            if self.get_collision(move_x, move_y).colliderect(rect):
                return 0, 0
        return move_x, move_y


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.gravity = 1
        self.action = 'idle'
        self.side = 'right'
        self.anim = Animation('maps/player.json', ['idle', 'walk', 'jump', 'slash'], self.action)
        self.image = pg.Surface((0, 0))
        self.anim.update(self, self.action, self.side)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        center1 = self.game.camera.apply(self).center
        center2 = self.game.camera.apply(self.game.player).center
        d_y = abs(center1[1] - center2[1])
        distance = vec(center1).distance_to(
            vec(center2))
        movement = 0
        if 300 > distance > TILE_SIZE > d_y:
            if center1[0] > center2[0]:
                movement -= 2
            else:
                movement += 2
        if self.gravity < 10:
            self.gravity += 0.5
        movement = self.collide_x(self.game.walls, movement)
        self.gravity = self.collide_y(self.game.walls, self.gravity)
        movement = self.collide_x(self.game.player, movement)
        self.gravity = self.collide_y(self.game.player, self.gravity)
        if movement > 0:
            self.side = 'right'
            self.action = 'walk'
        elif movement < 0:
            self.side = 'left'
            self.action = 'walk'
        else:
            self.action = 'idle'

        if self.gravity > 1:
            self.action = 'jump'
        if distance < TILE_SIZE * 1.8:
            self.action = 'slash'
        self.rect.x += movement
        self.rect.y += self.gravity
        self.anim.update(self, self.action, self.side)
        if self.rect.y > self.game.map.height:
            self.kill()

    def get_collision_x(self, movement):
        collision = self.rect.copy()
        collision.x += movement
        return collision

    def get_collision_y(self, movement):
        collision = self.rect.copy()
        collision.y += movement
        return collision

    def collide_x(self, tiles, movement):
        if isinstance(tiles, Player):
            if self.get_collision_x(movement).colliderect(tiles.collision_rect()):
                return 0
        else:
            for rect in tiles:
                if self.get_collision_x(movement).colliderect(rect):
                    return 0
        return movement

    def collide_y(self, tiles, movement):
        if isinstance(tiles, Player):
            if self.get_collision_y(movement).colliderect(tiles.collision_rect()):
                return 0
        else:
            for rect in tiles:
                if self.get_collision_y(movement).colliderect(rect):
                    self.gravity = 1
                    return 0
        return movement


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
