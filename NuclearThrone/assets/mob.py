import pygame


class Mob(pygame.sprite.Sprite):

    def __init__(self, game, x, y):
        self.game = game
        self.group = self.game.mobs
        pygame.sprite.Sprite.__init__(self, self.group)
        self.image = pygame.Surface((16, 16))
        self.image.blit(self.game.spritesheet, (0, 0), (368, 48, 16,16))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
