from pygame.math import Vector2 as vec

from Multimedia.tilemap import *


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.sprites, game.main
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.action = 'Idle'
        self.side = 'right'
        self.anim = Animation(self, 'player')
        self.image = pg.Surface((0, 0))
        self.anim.update(self.action, self.side)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.gravity = 0
        self.flying = False
        self.air_timer = 0
        self.hit_timer = 0
        self.U, self.D, self.L, self.R, self.fire = False, False, False, False, False
        self.health_point = 100
        self.hit = None
        self.get_hit = False
        self.health_bar = HealthBar(self, 32, 6)
        self.num_1, self.num_2, self.num_3 = True, False, False

    def update(self):
        self.health_bar.update()
        if not self.health_point == 0:
            if self.flying:
                self.air_timer += 1
            movement = 0
            if self.L:
                movement = -3
            elif self.R:
                movement = 3
            if self.gravity < 10:
                self.gravity += 0.5
            movement, self.gravity = self.check_collision(movement)
            if movement == 0:
                self.action = 'Idle'
            else:
                self.action = 'Run'
            if self.gravity >= 1 or self.gravity < -1:
                self.action = 'Jump'
            if self.D and not self.fire:
                self.action = 'BlockIdle'
            if self.get_hit:
                self.get_hit = False
                if self.action == 'BlockIdle':
                    self.action = 'Block'
                else:
                    self.health_point -= 10
                    self.action = 'Hurt'
                if self.health_point == 0:
                    self.action = 'Death'
            if self.fire and not self.D:
                if pg.time.get_ticks() - self.hit_timer > 1000:
                    self.hit_timer = pg.time.get_ticks()
                    Bullet(self.game, self.rect.x, self.rect.y, self.side)
                # if self.num_1:
                #     self.action = 'Attack'
                # elif self.num_2:
                #     self.action = 'Attack'
                # else:
                #     self.action = 'Attack'
                # if 'Attack' not in self.anim.action or ('Attack' in self.anim.action and self.anim.frame == len(
                #         self.anim.animation[self.anim.action]) - 1):
                #     if self.side == 'left':
                #         self.hit = self.get_collision().copy().move(-TILE_SIZE / 2, 0)
                #     else:
                #         self.hit = self.get_collision().copy().move(TILE_SIZE / 2, 0)

            if self.anim.action in ['Block', 'Hurt', 'Death', 'Attack1', 'Attack2', 'Attack3']:
                movement = 0
                if self.anim.frame < len(self.anim.animation[self.anim.action]) - 1:
                    self.action = self.anim.action
            else:
                if self.L:
                    self.side = 'left'
                if self.R:
                    self.side = 'right'

            self.rect.x += movement
            self.rect.y += self.gravity
            if self.rect.y > self.game.map.height:
                self.end_game()
        else:
            self.action = 'Death'
        self.anim.update(self.action, self.side)
        if 'Attack' in self.anim.action:
            self.attack()

    def attack(self):
        if self.hit is not None:
            for mob in self.game.mobs:
                if self.hit.colliderect(mob.get_collision()):
                    if self.anim.frame == len(self.anim.animation[self.anim.action]) - 1:
                        mob.get_hit = True
                        self.hit = None
                        return

    def get_collision(self):
        return pg.Rect(self.rect.x + (self.rect.width - TILE_SIZE) / 2,
                       self.rect.y + (self.rect.height - TILE_SIZE), TILE_SIZE, TILE_SIZE)

    def check_collision(self, movement):
        movement = self.horizontal_collide(self.game.walls, movement)
        self.gravity = self.vertical_collide(self.game.walls, self.gravity)
        # movement = self.collide_x(self.game.mobs, movement)
        # self.gravity = self.collide_y(self.game.mobs, self.gravity)
        movement, self.gravity = self.xy_collide(self.game.walls, movement, self.gravity)
        return movement, self.gravity

    def horizontal_collide(self, tiles, movement):
        for rect in tiles:
            if self.get_collision_x(movement).colliderect(rect.get_collision()):
                return 0
        return movement

    def vertical_collide(self, tiles, movement):
        for rect in tiles:
            if self.get_collision_y(movement).colliderect(rect.get_collision()):
                self.air_timer = 0
                return 0
        return movement

    def get_collision_x(self, movement):
        collision = self.get_collision().copy()
        collision.x += movement
        return collision

    def get_collision_y(self, movement):
        collision = self.get_collision().copy()
        collision.y += movement
        return collision

    def get_collision_xy(self, move_x, move_y):
        collision = self.get_collision().copy()
        collision.x += move_x
        collision.y += move_y
        return collision

    def xy_collide(self, tiles, move_x, move_y):
        for rect in tiles:
            if self.get_collision_xy(move_x, move_y).colliderect(rect.get_collision()):
                return 0, 0
        return move_x, move_y

    def end_game(self):
        self.game.playing = False


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y, filename):
        self.groups = game.sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.gravity = 1
        self.action = 'Idle'
        self.face_to = 'right'
        self.anim = Animation(self, filename)
        self.image = pg.Surface((0, 0))
        self.anim.update(self.action, self.face_to)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_point = 100
        self.get_hit = False
        self.hit_timer = None
        self.hit = None
        self.health_bar = HealthBar(self, 32, 6)

    def update(self):
        self.health_bar.update()
        center = self.game.camera.apply(self).center
        player_center = self.game.camera.apply(self.game.player).center
        vertical_distance = abs(center[1] - player_center[1])
        self_to_player = vec(center).distance_to(
            vec(player_center))
        movement = 0
        if 300 > self_to_player > TILE_SIZE > vertical_distance:
            if center[0] > player_center[0]:
                movement -= 2
            else:
                movement += 2
        if self.gravity < 10:
            self.gravity += 0.5
        movement = self.horizontal_collide(self.game.walls, movement)
        self.gravity = self.vertical_collide(self.game.walls, self.gravity)
        if movement > 0:
            self.action = 'Run'
        elif movement < 0:
            self.action = 'Run'
        else:
            self.action = 'Idle'
        if self.gravity > 1:
            self.action = 'Jump'
        if self.rect.center[0] - self.game.player.rect.center[0] < 0:
            self.face_to = 'right'
        else:
            self.face_to = 'left'

        if self.get_hit:
            self.get_hit = False
            self.health_point -= 50
            self.action = 'Hurt'
        if self.health_point == 0:
            self.action = 'Death'

        if self_to_player < TILE_SIZE * 2:
            if self.hit_timer is None:
                self.hit_timer = pg.time.get_ticks()
            if pg.time.get_ticks() - self.hit_timer > 1500 and not self.action == 'Hurt':
                self.action = 'Attack'
                self.hit_timer = None
        elif self.hit_timer:
            self.hit_timer -= 500
        else:
            self.hit_timer = None
        if 'Attack' in self.action:
            if self.face_to == 'left':
                self.hit = self.get_collision().copy().move(-TILE_SIZE // 2, 0)
            else:
                self.hit = self.get_collision().copy().move(TILE_SIZE // 2, 0)
        if self.hit is not None and self.hit.colliderect(
                self.game.player.get_collision()):
            if 'Attack' in self.anim.action and self.anim.frame == len(
                    self.anim.animation[self.anim.action]) - 1:
                self.game.player.get_hit = True
                self.hit = None

        if self.anim.action in ['Hurt', 'Death', 'Attack']:
            movement = 0
            self.hit_timer = None
            if self.anim.frame < len(self.anim.animation[self.anim.action]) - 1:
                self.action = self.anim.action

        self.rect.x += movement
        self.rect.y += self.gravity
        self.anim.update(self.action, self.face_to)

    def get_collision(self):
        return pg.Rect(self.rect.x + 50,
                       self.rect.y + 50, 50, 50)

    def get_collision_x(self, movement):
        collision = self.get_collision().copy()
        collision.x += movement
        return collision

    def get_collision_y(self, movement):
        collision = self.get_collision().copy()
        collision.y += movement
        return collision

    def horizontal_collide(self, tiles, movement):
        if isinstance(tiles, Player):
            if self.get_collision_x(movement).colliderect(tiles.get_collision()):
                return 0
        else:
            for rect in tiles:
                if self.get_collision_x(movement).colliderect(rect):
                    return 0
        return movement

    def vertical_collide(self, tiles, movement):
        if isinstance(tiles, Player):
            if self.get_collision_y(movement).colliderect(tiles.get_collision()):
                return 0
        else:
            for rect in tiles:
                if self.get_collision_y(movement).colliderect(rect):
                    self.gravity = 1
                    return 0
        return movement


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

    def get_collision(self):
        return self.rect


class HealthBar:
    def __init__(self, entity, w, h):
        self.image = pg.Surface((w, h))
        self.w = w
        self.h = h
        self.entity = entity
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.center = self.entity.rect.center
        self.rect.y -= 32
        self.image.fill(RED)
        self.image.fill(GREEN, pg.Rect(0, 0, self.entity.health_point / 100 * self.w, self.h))
        pg.draw.rect(self.image, YELLOW, (0, 0, self.w, self.h), 1)


class Item(pg.sprite.Sprite):
    def __init__(self, game, x, y, item_type):
        self.groups = game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.type = item_type
        self.image = game.item_imgs[item_type]
        self.rect = self.image.get_rect()
        self.game = game
        self.rect.topleft = (x, y)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        self.group = game.bullets
        pg.sprite.Sprite.__init__(self, self.group)
        self.image = pg.image.load(BULLET_IMG).convert()
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.direction = direction
        if self.direction == 'left':
            self.image = pg.transform.flip(self.image, True, False)

    def update(self):
        if self.direction == 'left':
            self.rect.x -= 2
        if self.direction == 'right':
            self.rect.x += 2


