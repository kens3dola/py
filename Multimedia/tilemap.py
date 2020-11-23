import pygame as pg
from Multimedia.settings import *
import pytmx
import json, math, os


class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILE_SIZE
        self.height = self.tileheight * TILE_SIZE


class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface, only_visible):
        ti = self.tmxdata.get_tile_image_by_gid
        if only_visible:
            for layer in self.tmxdata.visible_layers:
                self.blit_map(layer, surface, ti)
        else:
            for layer in self.tmxdata.layers:
                self.blit_map(layer, surface, ti)

    def blit_map(self, layer, surface, ti):
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid, in layer:
                tile = ti(gid)
                if tile:
                    surface.blit(tile, (x * self.tmxdata.tilewidth,
                                        y * self.tmxdata.tileheight))

    def make_map(self, only_visible):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface, only_visible)
        return temp_surface


class Animation:
    def __init__(self, entity, name):
        self.entity = entity
        self.animation = {}
        for action in os.listdir(os.path.join('img', name)):
            self.animation[action] = []
            for img in os.listdir(os.path.join('img', name, action)):
                img = pg.image.load(os.path.join('img', name, action, img)).convert()
                img.set_colorkey(BLACK)
                if img is not None:
                    self.animation[action].append(img)
        self.action = "Idle"
        self.frame = 0
        self.last_updated = pg.time.get_ticks()
        self.duration = {'Attack': 100, 'Attack1': 100, 'Attack2': 100, 'Attack3': 100, 'Idle': 100, 'Run': 100,
                         'Jump': 600,
                         'Hurt': 100, 'BlockIdle': 100, 'Block': 100, 'Death': 300}

    def update(self, action, side):
        if self.action == "Death" and self.frame == len(self.animation['Death']) - 1:
            self.entity.kill()
        else:
            now = pg.time.get_ticks() - self.last_updated
            if 'Attack' in self.action:
                if now > self.duration[self.action]:
                    self.frame += 1
                    if self.frame >= len(self.animation[self.action]):
                        self.action = action
                        self.frame = 0
                    else:
                        self.frame = self.frame % len(self.animation[self.action])
                        self.last_updated = pg.time.get_ticks()
            if 'Attack' not in self.action:
                if self.action == action:
                    if now > self.duration[self.action]:
                        self.frame += 1
                        self.frame = self.frame % len(self.animation[self.action])
                        self.last_updated = pg.time.get_ticks()
                else:
                    self.action = action
                    self.frame = 0
            try:
                image = self.animation[self.action][self.frame]
            except IndexError:
                image = self.animation[self.action][0]
            if side == 'left':
                self.entity.image = pg.transform.flip(image, True, False)
            else:
                self.entity.image = pg.transform.flip(image, False, False)


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.bg_camera = self.camera.copy()
        self.width = width
        self.height = height
        self.offset_x = 0
        self.offset_y = 0
        self.bg_x = 0

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        rect = rect.move(self.camera.topleft)
        # x =  (self.camera.x - self.offset_x)
        # rect.x += x
        # y =  (self.camera.y - self.offset_y)
        # print(y)
        # rect.y += y
        return rect

    def update(self, target):
        self.offset_x, self.offset_y = self.camera.center
        x = -target.rect.center[0] + int(WIDTH / 2)
        y = -target.rect.center[1] + int(HEIGHT / 2)
        # limit scrolling to map size
        x = min(0, x)  # leftd
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        x = (x - self.camera.x)/20
        y = (y - self.camera.y)/20
        x= round(x)
        y=round(y)
        self.bg_x += x / 2
        if self.bg_x <= -WIDTH:
            self.bg_x = 0
        elif self.bg_x > 0:
            self.bg_x = -WIDTH
        self.bg_x = int(self.bg_x)
        self.camera.x += x
        self.camera.y += y


class Minimap:
    def __init__(self, game):
        self.game = game
        # self.img = pg.image.load('img/minimap.png').convert()
        self.img = pg.Surface((self.game.map.width // 10, self.game.map.height // 10))
        pg.transform.scale(self.game.map_img, (self.game.map.width // 10, self.game.map.height // 10), self.img)
        self.r = self.img.get_rect()
        self.image = pg.Surface((self.r.width // 2.5, self.r.height // 2))
        self.rect = self.image.get_rect()
        self.player = pg.Surface((3, 3))
        self.player.fill(GREEN)
        self.mob = pg.Surface((3, 3))
        self.mob.fill(RED)
        self.min_pos_x = self.r.width - self.rect.width
        self.min_pos_y = self.r.height - self.rect.height

    def update(self):
        camera_position_topleft = self.game.camera.camera.topleft
        self.rect.topleft = (
            min(-camera_position_topleft[0] / self.game.map.width * self.r.width, self.min_pos_x),
            min(-camera_position_topleft[1] / self.game.map.height * self.r.height, self.min_pos_y))
        self.image.blit(self.img, (0, 0), self.rect)

        # draw object position to minimap
        for sprite in self.game.sprites:
            sprite_center = self.game.camera.apply(sprite).center
            destination = ((sprite_center[0]-16) / self.game.map.width * self.r.width,
                           (sprite_center[1] + 10) / self.game.map.height * self.r.height)
            if sprite in self.game.main:
                self.image.blit(self.player, destination)
            else:
                self.image.blit(self.mob, destination)
