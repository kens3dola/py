# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 1
# Project setup
# Video link: https://youtu.be/3UxnelT9aCo
import pygame as pg
import sys
from Multimedia.demo.settings import *
from Multimedia.demo.sprites import *


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()

    def load_data(self):
        pass

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.player = Player(self, 100, 100)
        for x in range(1, 20):
            Wall(self, x, 10)
        self.offset = [0, 0]

    def run(self):
        # game loop - set self.playing = False to end the game
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
        # update portion of the game loop
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.offset = [0, 0]
        if self.player.rect.x > 200:
            self.offset[0] -= self.player.movement[0]
        # if self.player.rect.y > 100:
        #     self.offset[1] -= self.player.movement[1]
        self.screen.blit(self.player.image, self.player.rect)
        pg.draw.rect(self.screen, self.player.color, self.player.rect, 1)
        for wall in self.walls:
            pg.draw.rect(self.screen, wall.color, wall.rect, 1)
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_LEFT:
                    self.player.L = True
                if event.key == pg.K_RIGHT:
                    self.player.R = True
                if event.key == pg.K_UP:
                    self.player.U = True
                if event.key == pg.K_DOWN:
                    self.player.D = True
            if event.type == pg.KEYUP:
                if event.key == pg.K_LEFT:
                    self.player.L = False
                if event.key == pg.K_RIGHT:
                    self.player.R = False
                if event.key == pg.K_UP:
                    self.player.U = False
                if event.key == pg.K_DOWN:
                    self.player.D = False

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass


# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
