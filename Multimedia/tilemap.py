import pygame as pg
from Multimedia.settings import *
import pytmx
import json, math


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

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Animation:
    def __init__(self, filename, set, action):
        with open(filename) as f:
            self.data = json.load(f)
        self.image = pg.image.load(self.data['image'])
        self.image.set_colorkey((0, 0, 0))
        self.tiles = {}
        self.tile_height = self.data['tileheight']
        self.tile_width = self.data['tilewidth']
        self.tile_row = math.sqrt(self.data['tilecount'])
        self.animation = {}
        for i, state in enumerate(set):
            self.animation[state] = self.load_animation(self.data['tiles'][i])
        self.action = action
        self.frame = 0
        self.last_updated = pg.time.get_ticks()

    def load_animation(self, tiles):
        animation = tiles['animation']
        anim_set = []
        for tile in animation:
            id = tile['tileid']
            anim_set.append(id)
            if id not in self.tiles:
                self.tiles[id] = self.get_sprite(id, self.tile_width, self.tile_height)
        return anim_set

    def get_sprite(self, tile, w, h):
        x = (tile % self.tile_row) * self.tile_width + self.data['margin']
        y = (tile // self.tile_row) * self.tile_height + self.data['margin']
        sprite = pg.Surface((w, h))
        sprite.set_colorkey((0, 0, 0))
        sprite.blit(self.image, (0, 0), (x, y, w, h))
        return sprite

    def update(self, entity, action, side):
        now = pg.time.get_ticks() - self.last_updated
        if self.action == 'slash':
            if now > 200:
                self.frame += 1
                if self.frame >= len(self.animation[self.action]):
                    self.action = action
                    self.frame = 0
                else:
                    self.frame = self.frame % len(self.animation[self.action])
                    self.last_updated = pg.time.get_ticks()
        if self.action != 'slash':
            if self.action == action:
                if now > 100:
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
            entity.image = pg.transform.flip(self.tiles[image], True, False)
        else:
            entity.image = pg.transform.flip(self.tiles[image], False, False)


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.offset_x = 0
        self.offset_y = 0

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + int(WIDTH / 2)
        y = -target.rect.y + int(HEIGHT / 2)
        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)
