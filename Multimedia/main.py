import pygame as pg
import sys
from Multimedia.sprites import *
from Multimedia.settings import *
from Multimedia.tilemap import *


class Game:
    def __init__(self):
        pg.init()
        self.display = pg.display.set_mode((int(WIDTH * 2), int(HEIGHT * 2)))
        self.screen = pg.Surface((WIDTH, HEIGHT))
        self.pause_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.pause_screen.fill((0, 0, 0, 180))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()
        self.playing = True
        self.paused = False

    def load_data(self):
        self.map = TiledMap('maps/map.tmx')
        self.map_img = self.map.make_map(True)
        self.map_rect = self.map_img.get_rect()
        self.map_img.set_colorkey(BLACK)
        self.item_imgs = {}
        # for item in Items:
        #     self.item_imgs[item] = pg.image.load('img/item/' + item + '.png').convert()
        #     self.item_imgs[item].set_colorkey(BLACK)

    def new(self):
        self.main = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.sprites = pg.sprite.Group()
        self.health_bar = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == "actor":
                self.player = Player(self, tile_object.x, tile_object.y)
            if tile_object.name == "soil":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            # if tile_object.name == "Goblin":
            #     Mob(self, tile_object.x, tile_object.y, 'Goblin')
            # if tile_object.name == "Mushroom":
            #     Mob(self, tile_object.x, tile_object.y, 'Mushroom')
            # if tile_object.name == "Flying eye":
            #     Mob(self, tile_object.x, tile_object.y, 'Flying eye')
            # if tile_object.name == "Skeleton":
            #     Mob(self, tile_object.x, tile_object.y, 'Skeleton')
            # if tile_object.name in self.item_imgs:
            #     Item(self, tile_object.x, tile_object.y, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height)
        self.bg_img = pg.transform.scale(pg.image.load('img/Background.png').convert(), (WIDTH, HEIGHT))
        self.camera_rect = pg.Rect(0, 0, WIDTH, HEIGHT)
        self.camera_rect2 = pg.Rect(WIDTH, 0, WIDTH, HEIGHT)
        self.minimap = Minimap(self)

    def run(self):
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.sprites.update()
        self.bullets.update()
        self.camera.update(self.player)
        self.minimap.update()
        self.camera_rect.x = self.camera.bg_x
        self.camera_rect2.x = self.camera.bg_x + WIDTH

    def draw(self):
        self.screen.blit(self.bg_img, self.camera_rect)
        self.screen.blit(self.bg_img, self.camera_rect2)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            self.screen.blit(sprite.health_bar.image, self.camera.apply_rect(sprite.health_bar.rect))
        for sprite in self.items:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        for bullet in self.bullets:
            self.screen.blit(bullet.image, self.camera.apply(bullet))
        '''   debug    '''
        # for sprite in self.walls:
        #     pg.draw.rect(self.screen, BLACK, self.camera.apply(sprite), 1)
        # for sprite in self.sprites:
        #     pg.draw.rect(self.screen, WHITE, self.camera.apply_rect(sprite.collision_rect()), 1)

        # draw minimap
        self.screen.blit(self.minimap.image, (MINIMAP_POS, 10))

        if self.paused:
            self.screen.blit(self.pause_screen, (0, 0))
            self.draw_text('paused', 50, RED, WIDTH // 2, HEIGHT // 2)
        # self.display.blit(self.screen, (0, 0))
        self.display.blit(pg.transform.scale(self.screen, (int(WIDTH * 2), int(HEIGHT * 2))), (0, 0))
        pg.display.update()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

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
                    if self.player.air_timer <= 20 and 'Attack' not in self.player.anim.action and 'Hurt' not in self.player.anim.action:
                        self.player.flying = True
                        self.player.gravity = -7
                if event.key == pg.K_s:
                    self.player.D = True
                if event.key == pg.K_SPACE:
                    self.player.fire = True
                if event.key == pg.K_1:
                    self.player.num_1 = True
                    self.player.num_3 = False
                    self.player.num_2 = False
                if event.key == pg.K_2:
                    self.player.num_2 = True
                    self.player.num_3 = False
                    self.player.num_1 = False
                if event.key == pg.K_3:
                    self.player.num_3 = True
                    self.player.num_2 = False
                    self.player.num_2 = False
                if event.key == pg.K_p:
                    self.paused = not self.paused
                    print(self.paused)
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
                    self.player.fire = False


g = Game()
g.new()
g.run()
