import pygame as pg
from settings import *
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

    def render(self, surface, layers):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.layers:
            if layer.name in layers:
                self.blit_map(layer, surface, ti)

    def blit_map(self, layer, surface, ti):
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid, in layer:
                tile = ti(gid)
                if tile:
                    surface.blit(tile, (x * self.tmxdata.tilewidth,
                                        y * self.tmxdata.tileheight))

    def make_map(self, layers):
        temp_surface = pg.Surface((self.width, self.height))
        temp_surface.fill(WHITE)
        self.render(temp_surface, layers)
        return temp_surface


class Animation:
    def __init__(self, entity, name):
        self.entity = entity
        self.animation = {}
        for action in os.listdir(os.path.join('img', name)):
            self.animation[action] = []
            for img in os.listdir(os.path.join('img', name, action)):
                img = pg.image.load(os.path.join('img', name, action, img)).convert()
                if name == 'King' and img.get_rect().width == 160:
                    img = img.subsurface(16, 0, 128, 128)
                if img is not None:
                    self.animation[action].append(img)
        self.action = "Idle"
        self.frame = 0
        self.last_updated = pg.time.get_ticks()
        self.duration = {'Attack': 100, 'Attack1': 100, 'Attack2': 100, 'Attack3': 100, 'Idle': 100, 'Run': 80,
                         'Jump': 60,
                         'Hurt': 500, 'BlockIdle': 100, 'Block': 100, 'Death': 300, 'Walk': 80, 'Combo': 80}
        self.last_side = 'left'

    def update(self, action, side):
        now = pg.time.get_ticks() - self.last_updated
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
        except KeyError:
            image = self.animation['Idle'][0]
        if self.action in ['Attack', 'Combo']:
            side = self.last_side
        if side == 'left':
            self.entity.image = pg.transform.flip(image, True, False)
        else:
            self.entity.image = pg.transform.flip(image, False, False)
        self.last_side = side


class Camera:
    def __init__(self, game, width, height):
        self.game = game
        self.camera = pg.Rect(0, 0, width, height)
        self.bg_camera = self.camera.copy()
        self.width = width
        self.height = height
        self.bg_x = 0

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        rect = rect.move(self.camera.topleft)
        return rect

    def apply_point(self, point):
        x = point[0] / SCALE
        y = point[1] / SCALE
        return [x - self.camera.x, y - self.camera.y]

    def update(self, target):
        x = -target.rect.center[0] + int(WIDTH / 2)
        y = -target.rect.center[1] + int(HEIGHT / 2)
        # limit scrolling to map size
        x = min(0, x)  # leftd
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        self.game.screen_rect.topleft = (-x, -y)
        x = x - self.camera.x
        y = y - self.camera.y
        if x > 0:
            if x >= 20:
                x = x / 20
            elif x >= 1:
                x = 1
        else:
            if x <= -20:
                x = x / 20
            elif x <= -1:
                x = -1
        if y > 0:
            if y >= 20:
                y = y / 20
            elif y >= 1:
                y = 1
        else:
            if y <= -20:
                y = y / 20
            elif y <= -1:
                y = -1
        self.bg_x += x / 2
        self.camera.x += x
        self.camera.y += y


class Minimap:
    def __init__(self, game):
        self.game = game
        self.img = pg.Surface((self.game.map.width // MINIMAP_X, self.game.map.height // MINIMAP_Y))
        self.size = (self.game.map.width // MINIMAP_X, self.game.map.height // MINIMAP_Y)
        pg.transform.scale(self.game.minimap_img, self.size, self.img)
        self.img.set_colorkey(WHITE)
        self.r = self.img.get_rect()  # 1/12 map
        self.image = pg.Surface((50, 30))  # 1/20 map
        self.rect = self.image.get_rect()

        self.player = pg.Surface((1, 2))
        self.player.fill(GREEN)
        self.mob = pg.Surface((1, 2))
        self.mob.fill(RED)
        self.min_pos_x = self.r.width - self.rect.width
        self.min_pos_y = self.r.height - self.rect.height
        self.sc_rect = pg.Rect(0, 0, WIDTH, HEIGHT)

    def update(self):
        pg.transform.scale(self.game.minimap_img, self.size, self.img)
        camera_position_topleft = self.game.camera.camera.topleft
        self.rect.topleft = (
            min(-camera_position_topleft[0] / self.game.map.width * self.r.width, self.min_pos_x),
            min(-camera_position_topleft[1] / self.game.map.height * self.r.height, self.min_pos_y))

        for sprite in self.game.sprites:
            sprite_rect = sprite.rect
            # if sprite_rect.colliderect(self.sc_rect):
            destination = (sprite_rect.center[0] / self.game.map.width * self.r.width,
                           sprite_rect.center[1] / self.game.map.height * self.r.height)
            if sprite in self.game.main:
                self.img.blit(self.player, destination)
            else:
                self.img.blit(self.mob, destination)

        self.image.fill(WHITE)
        self.image.blit(self.img, (0, 0), self.rect)
