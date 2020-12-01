import pygame
from pygame import *
from Multimedia.settings import *


class TitleScene(object):

    def __init__(self, game):
        super(TitleScene, self).__init__()
        self.game = game
        self.font = pygame.font.SysFont('Arial', 15)
        self.font_pos = (WIDTH//2,HEIGHT//2-15)
        self.sfont = pygame.font.SysFont('Arial', 10)
        self.sfont_pos = (WIDTH//2, HEIGHT//2+10)

    def render(self, screen):
        screen.fill(BLACK)
        text1 = self.font.render('Tiled base game', False, (255, 255, 255))
        text1_rect = text1.get_rect()
        text2 = self.sfont.render('> press p to start <', False, (255, 255, 255))
        text2_rect = text2.get_rect()
        text1_rect.midtop = self.font_pos
        text2_rect.midtop = self.sfont_pos
        screen.blit(text1, text1_rect)
        screen.blit(text2, text2_rect)

    def update(self):
        pass

