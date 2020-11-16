import pygame, csv, os, json


class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.parse_sprite(image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))


class TileMap:
    def __init__(self, filename, spritesheet, index):
        self.tile_size = 16
        self.start_x, self.start_y = 0, 0
        self.tiles = []
        self.index = index
        self.spritesheetname = os.path.join('assets', spritesheet)
        self.spritesheet = pygame.image.load(self.spritesheetname).convert()
        self.map_w = 30 * 16
        self.map_h = 20 * 16
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.set_colorkey((0, 0, 0))
        self.load_tiles(filename)

    def draw_map(self, surface):
        surface.blit(self.map_surface, (0, 0))

    def read_csv(self, filename):
        with open(os.path.join('assets', 'tilemap', filename)) as data:
            data = json.load(data)['layers'][self.index]['data']
        return data

    def load_tiles(self, filename):
        data = self.read_csv(filename)
        for y in range(20):
            for x in range(30):
                ind = data[x + y * 30]
                if ind != 0:
                    ind -= 1
                    self.tiles.append(pygame.Rect(x * 16, y * 16, 16, 16))
                    self.map_surface.blit(self.spritesheet, (x * 16, y * 16), (ind % 32 * 16, ind // 32 * 16, 16, 16))

    def get_tiles(self):
        return self.tiles
