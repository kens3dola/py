import pygame as pg


class Entity:
    def __init__(self, x, y, animation, tile_images):
        self.x = x
        self.y = y
        self.frame = 0
        self.action = 'idle'
        self.animation = animation
        self.tile_images = tile_images
        self.face_right = False
        self.dead = False
        self.hp = 5
        self.shot_time = 0
    def get_rect(self):
        return pg.Rect(self.x, self.y, 16, 16)

    def render(self, offside, screen):
        if not self.dead:
            image_id = self.animation[self.action][self.frame]
            image = self.tile_images[self.action][image_id]
            screen.blit(pg.transform.flip(image, self.face_right, False), (self.x - offside[0], self.y - offside[1]))

    def update(self, player_rect):
        if not self.dead:
            print(self.shot_time)
            if self.action == 'hit':self.shot_time+=1
            if self.shot_time > 20:
                self.action = 'idle'
                self.shot_time =0
            movement = 0;
            if abs(self.x - player_rect.x) < 150:
                if player_rect.x > self.x:
                    movement = 0.5
                    self.face_right = True
                if player_rect.x < self.x:
                    movement = -0.5
                    self.face_right = False
            self.x += movement
            self.frame += 1
            if self.frame >= len(self.animation[self.action]):
                self.frame = 0

    def attack(self, player_rect, hp):
        if not self.dead:
            if self.get_rect().colliderect(player_rect):
                if self.face_right:
                    self.x -= 5
                else:
                    self.x += 5
                hp -= 5
        return hp

    def rip(self):
        self.dead = True
        self.x = -50

    def be_shot(self):
        self.action = 'hit'
        self.shot_time = 0
        self.frame = 0
        if self.hp>0:
            self.hp -= 1
        else:
            self.rip()