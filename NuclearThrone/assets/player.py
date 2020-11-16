import math

import pygame

from NuclearThrone.assets.spritesheet.spritesheet import Spritesheet


class Bullet:
    def __init__(self, rect, destination, img):
        self.rect = rect
        self.destination = [destination[0] // 2, destination[1] // 2]
        self.stop = False
        self.stop_time = 0
        self.img = img

    def update(self, tiles):
        if not self.stop:
            center = list(self.rect.center)
            delta_x = self.destination[0] - center[0]
            delta_y = self.destination[1] - center[1]
            step = math.sqrt((delta_y ** 2 + delta_x ** 2)) // 10
            if step > 0:
                x = delta_x // step
                y = delta_y // step
                x = self.collide_x(tiles, x)
                y = self.collide_y(tiles, y)
                center[0] += x
                center[1] += y
            else:
                self.stop = True
            self.rect.center = center
        else:
            self.stop_time += 1

    def draw(self, surface):
        if self.stop_time < 500:
            surface.blit(self.img, self.rect)

    def collide_x(self, tiles, movement):
        for rect in tiles:
            if self.rect.colliderect(rect):
                return 0
        return movement

    def collide_y(self, tiles, movement):
        for rect in tiles:
            if self.rect.colliderect(rect):
                return 0
        return movement


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.LEFT_KEY, self.RIGHT_KEY, self.UP_KEY, self.DOWN_KEY, self.FACING_LEFT = False, False, False, False, False
        my_sprite_sheet = Spritesheet('spritesheet.png', 'assets/spritesheet/object16x16.json')
        anim_set = my_sprite_sheet.parse_sprite(2, {'idle': [0, 1], 'walk': [2, 3, 4, 5, 6, 7]})
        self.idle_frames_left = anim_set['idle']
        self.walking_frames_left = anim_set['walk']
        self.idle_frames_right = []
        for frame in self.idle_frames_left:
            self.idle_frames_right.append(pygame.transform.flip(frame, True, False))
        self.walking_frames_right = []
        for frame in self.walking_frames_left:
            self.walking_frames_right.append(pygame.transform.flip(frame, True, False))

        self.rect = self.idle_frames_right[0].get_rect()
        self.rect.x = 160
        self.rect.y = 48
        self.current_frame = 0
        self.last_updated = 0
        self.state = 'idle'
        self.current_image = self.idle_frames_right[0]
        self.weapon = pygame.image.load('assets/weapon/weapon_spear.png')
        self.weapons = []
        self.pos = self.weapon.get_rect()

    def draw(self, display):
        display.blit(self.current_image, self.rect)
        self.draw_weapon(display)

    def draw_weapon(self, display):
        mouse = pygame.mouse.get_pos()
        deg = self.point_degrees(mouse, [self.rect.center[0] * 2, self.rect.center[1] * 2])
        self.img = pygame.transform.rotate(self.weapon, 360 - deg)
        self.pos = self.img.get_rect()
        if 360 - deg <= 90:
            self.pos.bottomright = self.rect.center
            self.pos.x += 4
            self.pos.y += 4
        elif 360 - deg <= 180:
            self.pos.topright = self.rect.center
            self.pos.x += 4
            self.pos.y -= 4
        elif 360 - deg <= 270:
            self.pos.topleft = self.rect.center
            self.pos.x -= 4
            self.pos.y -= 4
        elif 360 - deg <= 360:
            self.pos.bottomleft = self.rect.center
            self.pos.x -= 4
            self.pos.y += 4

        display.blit(self.img, self.pos)
        self.draw_weapons(display)

    def update(self, tiles):
        movement = [0, 0]
        if self.LEFT_KEY:
            self.FACING_LEFT = True
            movement[0] = -2
        elif self.RIGHT_KEY:
            self.FACING_LEFT = False
            movement[0] = 2
        if self.UP_KEY:
            movement[1] = -2
        elif self.DOWN_KEY:
            movement[1] = 2
        movement[0] = self.collide_x(tiles, movement[0])
        movement[1] = self.collide_y(tiles, movement[1])
        self.rect.x += movement[0]
        self.rect.y += movement[1]
        if movement[0] != 0 or movement[1] != 0:
            self.state = 'walk'
        else:
            self.state = 'idle'
        self.animate()
        for rect in self.weapons:
            rect.update(tiles)

    def shoot(self, destination):
        self.weapons.append(Bullet(self.pos, pygame.mouse.get_pos(), self.img))

    def draw_weapons(self, surface):
        for rect in self.weapons:
            rect.draw(surface)

    def collide_x(self, tiles, movement):
        for rect in tiles:
            if self.get_collision_x(movement).colliderect(rect):
                return 0
        return movement

    def collide_y(self, tiles, movement):
        for rect in tiles:
            if self.get_collision_y(movement).colliderect(rect):
                return 0
        return movement

    def animate(self):
        now = pygame.time.get_ticks()
        if self.state == 'idle':
            if now - self.last_updated > 250:
                self.last_updated = now
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames_left)
                if self.FACING_LEFT:
                    self.current_image = self.idle_frames_right[self.current_frame]
                elif not self.FACING_LEFT:
                    self.current_image = self.idle_frames_left[self.current_frame]
        else:
            if now - self.last_updated > 50:
                self.last_updated = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames_left)
                if self.FACING_LEFT:
                    self.current_image = self.walking_frames_right[self.current_frame]
                else:
                    self.current_image = self.walking_frames_left[self.current_frame]

    def get_collision_x(self, move_x):
        return pygame.Rect(self.rect.x + move_x, self.rect.y + 12, 16, 4)

    def get_collision_y(self, move_y):
        return pygame.Rect(self.rect.x, self.rect.y + 12 + move_y, 16, 4)

    def point_degrees(self, p_1, p_2):
        x = p_1[0] - p_2[0]
        y = p_1[1] - p_2[1]
        if x == 0: x = 0.01
        deg = math.degrees(math.atan(abs(y) / abs(x)))
        if x >= 0:
            if y >= 0:
                deg = 90 + deg
            else:
                deg = 90 - deg
        else:
            if y >= 0:
                deg = 270 - deg
            else:
                deg = 270 + deg
        return deg
