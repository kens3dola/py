import sys
from NuclearThrone.menu import *
from NuclearThrone.assets.spritesheet.spritesheet import Spritesheet
from NuclearThrone.assets.player import Player
from NuclearThrone.assets.tilemap.tiles import *
from NuclearThrone.assets.mob import Mob

class Game:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        self.running, self.playing = True, False
        self.UP, self.DOWN, self.START, self.BACK = False, False, False, False
        self.DISPLAY_W, self.DISPLAY_H = 480, 320
        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pygame.display.set_mode((self.DISPLAY_W * 2, self.DISPLAY_H * 2))
        self.BLACK, self.WHITE = (0, 0, 0), (255, 255, 255)
        self.main_menu = MainMenu(self)
        self.cur_menu = self.main_menu
        self.player = Player()
        self.spritesheet = pygame.image.load('assets/spritesheet.png')
        self.mobs = pygame.sprite.Group()
        Mob(self, 116, 64)
        self.tiles_map = TileMap("map.json", "spritesheet.png", 1)
        self.back_tiles_map = TileMap("map.json", "spritesheet.png", 0)
        self.top_tiles_map = TileMap("map.json", "spritesheet.png", 2)
        self.clock = pygame.time.Clock()
        self.cusor = pygame.transform.rotate(pygame.image.load('assets/weapon/weapon_knife.png'), 45)

    def game_loop(self):
        while self.playing:
            self.clock.tick(60)
            pygame.display.set_caption(str(self.clock.get_fps()))
            self.event_handling()
            if self.START:
                self.playing = False
            self.display.fill(self.BLACK)
            self.back_tiles_map.draw_map(self.display)
            self.tiles_map.draw_map(self.display)
            self.player.update(self.tiles_map.get_tiles())
            self.player.draw(self.display)
            self.top_tiles_map.draw_map(self.display)
            mouse_pos = pygame.mouse.get_pos()
            self.display.blit(self.cusor, [mouse_pos[0]/2, mouse_pos[1]/2])
            self.mobs.update()
            self.mobs.draw(self.display)
            self.scale_screen()

    def event_handling(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                sys.exit(1)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START = True
                if event.key == pygame.K_ESCAPE:
                    self.BACK = True
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.UP_KEY = True
                    self.UP = True
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player.DOWN_KEY = True
                    self.DOWN = True
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.LEFT_KEY = True
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.RIGHT_KEY = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.LEFT_KEY = False
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.RIGHT_KEY = False
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.UP_KEY = False
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player.DOWN_KEY = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                k1, k2, k3 = pygame.mouse.get_pressed()
                if k1:
                    self.player.shoot(pos)

    def reset_keys(self):
        self.UP, self.DOWN, self.BACK, self.START = False, False, False, False

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(None, size)
        text = font.render(text, True, self.WHITE)
        text_rect = text.get_rect()
        text_rect.center = (x, y)
        self.display.blit(text, text_rect)

    def scale_screen(self):
        pygame.display.update()
        self.window.blit(pygame.transform.scale(self.display, (self.DISPLAY_W * 2, self.DISPLAY_H * 2)), (0, 0))
        self.reset_keys()
