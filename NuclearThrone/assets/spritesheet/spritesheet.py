import pygame
import os
import json


class Spritesheet:

    def __init__(self, filename, meta_data):
        self.filename = os.path.join('assets', filename)
        self.spritesheet = pygame.image.load(self.filename).convert()
        with open(meta_data) as f:
            self.data = json.load(f)
        f.close()
        self.tile_h = self.data['tileheight']
        self.tile_w = self.data['tilewidth']
        self.columns = self.data['columns']

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey((0, 0, 0))
        sprite.blit(self.spritesheet, (0, 0), (x, y, w, h))
        return sprite

    def parse_sprite(self, index, anim_data):
        anim = self.data['tiles'][index]['animation']
        animation_set = {}
        for st in anim_data:
            animation_set[st] = []
            for frame in anim_data[st]:
                sprite = anim[frame]['tileid']
                x, y, w, h = sprite % self.columns * self.tile_w, sprite // self.columns * self.tile_h, self.tile_w, self.tile_h
                image = self.get_sprite(x, y, w, h)
                animation_set[st].append(image)
        return animation_set
