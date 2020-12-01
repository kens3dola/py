import pygame as pg
import sys
from sprites import *
from settings import *
from tilemap import *
from scenes import *
import random


def load_sound():
    sounds = {}
    for snd in os.listdir('sound'):
        sounds[snd] = pg.mixer.Sound(os.path.join('sound', snd))
    return sounds


class Game:
    def __init__(self):
        pg.init()
        self.menu = TitleScene(self)
        self.display = pg.display.set_mode((int(WIDTH * SCALE), int(HEIGHT * SCALE)))
        self.screen = pg.Surface((WIDTH, HEIGHT))
        self.pause_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.pause_screen.fill((0, 0, 0, 180))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.playing = True
        self.paused = True
        self.sprites = pg.sprite.Group()
        self.mob_names = ['Chick', 'Corp', 'Eye', 'Fly', 'Jell', 'Mosq', 'Mush', 'Snake']
        self.load_data('maps/mi.tmx')
        self.game_over = False

    def load_data(self, map_file):
        self.sprites = pg.sprite.Group()
        self.map = TiledMap(map_file)
        self.minimap_img = self.map.make_map(['minimap'])
        self.map_img = self.map.make_map(['deco', 'main', 'background'])
        self.map_rect = self.map_img.get_rect()
        self.map_img.set_colorkey(WHITE)
        self.main = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.health_bar = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.wall = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.floating_text = pg.sprite.Group()
        self.boss = None
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == "actor":
                self.player = Player(self, tile_object.x, tile_object.y)
            elif tile_object.name == "boss":
                self.boss = Boss(self, tile_object.x, tile_object.y)
            elif tile_object.name == "soil":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            elif tile_object.name == "mob":
                name = random.randint(0, len(self.mob_names) - 1)
                Mob(self, tile_object.x, tile_object.y, 'enemy/' + self.mob_names[name])
        self.camera = Camera(self, self.map.width, self.map.height)
        self.minimap = Minimap(self)
        self.screen_rect = pg.Rect(0, 0, WIDTH, HEIGHT)
        self.get_wall()
        self.sounds = load_sound()

    def run(self):
        self.sounds['background.wav'].play()
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            now = pg.time.get_ticks()
            if not self.paused:
                self.update()
                # print('update time:', pg.time.get_ticks() - now)
                now = pg.time.get_ticks()
            self.draw()
            # print('draw time', pg.time.get_ticks() - now)

    def quit(self):
        pg.quit()
        sys.exit()

    def get_wall(self):
        self.wall.empty()
        for wall in self.walls:
            if wall.get_collision().colliderect(self.screen_rect.inflate(WIDTH//2, HEIGHT//2)):
                self.wall.add(wall)

    def update(self):
        self.get_wall()
        self.sprites.update()
        self.bullets.update()
        self.camera.update(self.player)
        self.minimap.update()
        self.floating_text.update()

    def draw(self):
        self.screen.fill(DARK_GREY)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            self.screen.blit(sprite.health_bar.image, self.camera.apply_rect(sprite.health_bar.rect))
        # for sprite in self.items:
        #     self.screen.blit(sprite.image, self.camera.apply(sprite))
        for bullet in self.bullets:
            self.screen.blit(bullet.image, self.camera.apply(bullet))
        for text in self.floating_text:
            self.screen.blit(text.image, self.camera.apply(text))
        '''   debug    '''
        # for sprite in self.walls:
        #     pg.draw.rect(self.screen, BLACK, self.camera.apply(sprite), 1)
        # for sprite in self.sprites:
        #     pg.draw.rect(self.screen, WHITE, self.camera.apply_rect(sprite.get_collision()), 1)
        # if self.boss:
        #     pg.draw.rect(self.screen, WHITE, self.camera.apply_rect(self.boss.rect), 1)

        # draw minimap
        self.screen.blit(self.minimap.image, (MINIMAP_POS, 10))

        if self.paused:
            self.sounds['background.wav'].stop()
            self.screen.blit(self.pause_screen, (0, 0))
            if self.player.health_point <= 0:
                self.sounds['end_game.wav'].play()
                self.sounds['end_game.wav'].stop()
                self.draw_text('Game over', 50, RED, WIDTH // 2, HEIGHT // 2)
            else:
                self.menu.render(self.screen)

        self.display.blit(pg.transform.scale(self.screen, (int(WIDTH * SCALE), int(HEIGHT * SCALE))), (0, 0))
        pg.display.update()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(FONT, size)
        text_surface = font.render(text, False, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y - size)
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
                    if self.player.air_timer <= JUMP_ELAPSE and 'Attack' not in self.player.anim.action and 'Hurt' not in self.player.anim.action:
                        self.player.flying = True
                        self.player.gravity = JUMP_SPEED
                        self.sounds['jump.wav'].play()
                if event.key == pg.K_s:
                    self.player.D = True
                if event.key == pg.K_SPACE:
                    self.player.fire = True
                if event.key == pg.K_p:
                    self.paused = not self.paused
                    if self.game_over:
                        self.paused = False
                        self.load_data('maps/mi.tmx')
                        self.game_over = False
                    if self.paused:
                        self.sounds['background.wav'].stop()
                    else:
                        self.sounds['background.wav'].play()
                if event.key == pg.K_m:
                    self.load_data('maps/map.tmx')
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
g.run()
