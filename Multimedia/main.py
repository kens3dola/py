import pygame as pg
import sys
from Multimedia.sprites import *
from Multimedia.settings import *
from Multimedia.tilemap import *


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()

    def load_data(self):
        self.map = TiledMap('maps/map1.tmx')
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

    def new(self):
        self.sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == "player":
                self.player = Player(self, tile_object.x, tile_object.y)
            if tile_object.name == "ground":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == "mob":
                Mob(self, tile_object.x, tile_object.y)
        self.camera = Camera(self.map.width, self.map.height)

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.sprites.update()
        self.camera.update(self.player)

    def draw(self):
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        '''   debug    '''
        # for sprite in self.walls:
        #     pg.draw.rect(self.screen, BLACK, self.camera.apply(sprite), 1)
        # pg.draw.rect(self.screen, BLACK, self.camera.apply_rect(self.player.collision_rect()), 1)
        # pg.draw.rect(self.screen, RED, self.camera.apply(self.player), 1)
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_a:
                    self.player.L = True
                if event.key == pg.K_d:
                    self.player.R = True
                if event.key == pg.K_w:
                    if self.player.air_time <= 20:
                        self.player.in_air = True
                        self.player.gravity = -8
                if event.key == pg.K_s:
                    self.player.D = True
                if event.key == pg.K_SPACE:
                    self.player.slash = True
            if event.type == pg.KEYUP:
                if event.key == pg.K_a:
                    self.player.L = False
                if event.key == pg.K_d:
                    self.player.R = False
                if event.key == pg.K_w:
                    self.player.U = False
                if event.key == pg.K_s:
                    self.player.D = False
                if event.key == pg.K_SPACE:
                    self.player.slash = False


g = Game()
g.new()
g.run()
