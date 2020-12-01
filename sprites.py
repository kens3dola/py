from tilemap import *
import pygame as pg

class Boss(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.action = 'Idle'
        self.side = 'left'
        self.anim = Animation(self, 'King')
        self.image = pg.Surface((0, 0))
        self.anim.update(self.action, self.side)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.health_point = 1000
        self.gap = 35
        self.max_hp = 1000
        self.health_bar = HealthBar(self, 24, 4)
        self.gravity = 0
        self.attack_timer = pg.time.get_ticks()
        self.combo_timer = pg.time.get_ticks()
        self.debug = False
        self.get_hit = False

    def update(self):
        self.health_bar.update()
        if self.get_hit:
            self.health_point -= 10
            self.game.sounds['explosion.wav'].play()
            self.get_hit = False

        distance = self.game.player.rect.center[0] - self.get_collision().center[0]
        movement = 0
        if distance > BOSS_ATK_RANGE:
            movement = 2
        elif distance < -BOSS_ATK_RANGE:
            movement = -2
        self.gravity += 0.5
        movement = self.check_collision(movement)
        if movement > 0:
            self.action = 'Walk'
            self.side = 'right'
        elif movement < 0:
            self.action = 'Walk'
            self.side = 'left'
        else:
            self.action = 'Idle'
        if -BOSS_ATK_RANGE <= distance <= BOSS_ATK_RANGE and self.anim.action not in ['Attack', 'Combo']:
            if pg.time.get_ticks() - self.attack_timer > 3000:
                self.action = 'Attack'
                self.attack_timer = pg.time.get_ticks()
                BossAttack(self, self.side)
        if not self.anim.action == 'Attack':
            if pg.time.get_ticks() - self.combo_timer > 10000:
                self.action = 'Combo'
                self.combo_timer = pg.time.get_ticks()
                BossCombo(self)
        if self.anim.action in ['Block', 'Hurt', 'Death', 'Attack', 'Attack2', 'Attack3', 'Combo']:
            movement = 0
            if self.anim.frame < len(self.anim.animation[self.anim.action]) - 1:
                self.action = self.anim.action

        self.rect.x += movement
        self.rect.y += self.gravity
        self.anim.update(self.action, self.side)

    def check_collision(self, movement):
        movement = self.horizontal_collide(self.game.wall, movement)
        self.gravity = self.vertical_collide(self.game.wall, self.gravity)
        return movement

    def horizontal_collide(self, tiles, movement):
        for rect in tiles:
            if self.get_collision_x(movement).colliderect(rect.get_collision()):
                return 0
        return movement

    def vertical_collide(self, tiles, movement):
        for rect in tiles:
            if self.get_collision_y(movement).colliderect(rect.get_collision()):
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

    def get_collision(self):
        rect = pg.Rect(0, 0, 18, 38)
        rect.center = self.rect.center
        rect.y -= 11
        return rect


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
        self.gap = 24
        self.max_hp = 100
        self.health_bar = HealthBar(self, 24, 4)
        self.num_1, self.num_2, self.num_3 = True, False, False

    def update(self):
        self.health_bar.update()
        if not self.health_point <= 0:
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
                self.game.sounds['walk.wav'].play()
            if self.gravity >= 1 or self.gravity < -1:
                self.action = 'Jump'
            if self.get_hit:
                self.get_hit = False
                self.health_point -= 10
                self.game.sounds['death.wav'].play()
                FloatingText(self.game, self.rect.center[0], self.rect.center[1], WHITE, FLOAT_TEXT_SIZE, '-10')
                self.action = 'Hurt'
            if self.fire and not self.D:
                if pg.time.get_ticks() - self.hit_timer > 300:
                    self.hit_timer = pg.time.get_ticks()
                    Bullet(self.game, self.rect.x, self.rect.y, self.side)
                    self.game.sounds['shoot.wav'].play()
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
            self.end_game()
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
        movement = self.horizontal_collide(self.game.wall, movement)
        self.gravity = self.vertical_collide(self.game.wall, self.gravity)
        movement, self.gravity = self.xy_collide(self.game.wall, movement, self.gravity)
        return movement, self.gravity

    def horizontal_collide(self, tiles, movement):
        for rect in tiles:
            if self.get_collision_x(movement).colliderect(rect.get_collision()):
                return 0
        return movement

    def vertical_collide(self, tiles, movement):
        for rect in tiles:
            if self.get_collision_y(movement).colliderect(rect.get_collision()):
                if movement > 0:
                    self.flying = False
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
        self.game.paused = True
        self.game.game_over = True


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
        self.gap = 24
        self.max_hp = 100
        self.health_bar = HealthBar(self, 16, 3)
        self.auto_bullet = pg.time.get_ticks()
        self.is_update = True
        self.game_rect = pg.Rect(0, 0, WIDTH, HEIGHT)

    def update(self):
        if pg.time.get_ticks() - self.auto_bullet > 4000:
            AutoBullet(self.game, self.rect.x, self.rect.y, self.game.player.rect.center)
            self.auto_bullet = pg.time.get_ticks()
        if self.game.camera.apply(self).colliderect(self.game_rect):
            self.health_bar.update()
            center = self.game.camera.apply(self).center
            player_center = self.game.camera.apply(self.game.player).center
            vertical_distance = abs(center[1] - player_center[1])
            self_to_player = math.hypot(player_center[0] - center[0], player_center[1] - center[1])
            movement = 0
            if 50 > self_to_player > TILE_SIZE // 2 > vertical_distance:
                if center[0] > player_center[0]:
                    movement -= 1
                else:
                    movement += 1
            if self.gravity < 10:
                self.gravity += 0.5
            movement = self.horizontal_collide(self.game.wall, movement)
            self.gravity = self.vertical_collide(self.game.wall, self.gravity)
            if movement > 0:
                self.action = 'Run'
            elif movement < 0:
                self.action = 'Run'
            else:
                self.action = 'Idle'
            if self.gravity > 1:
                self.action = 'Run'
            elif self.gravity < 0:
                movement = 0
            if self.rect.center[0] - self.game.player.rect.center[0] < 0:
                self.face_to = 'left'
            else:
                self.face_to = 'right'

            if self.get_hit:
                self.get_hit = False
                self.health_point -= 25
                self.game.sounds['explosion.wav'].play()
                FloatingText(self.game, self.rect.center[0], self.rect.center[1], WHITE, FLOAT_TEXT_SIZE, '-25')
                self.action = 'Hurt'
            if self.health_point == 0:
                self.game.player.health_point += 10
                if self.game.player.health_point >100:
                    self.game.player.max_hp = self.game.player.health_point
                self.kill()

            if self_to_player < TILE_SIZE * 2:
                if self.hit_timer is None:
                    self.hit_timer = pg.time.get_ticks()
                if pg.time.get_ticks() - self.hit_timer > 1500 and not self.action == 'Hurt':
                    self.action = 'Attack'
                    self.hit_timer = pg.time.get_ticks()
                    if self.face_to == 'left':
                        self.hit = self.get_collision().copy().move(TILE_SIZE // 2, 0)
                    else:
                        self.hit = self.get_collision().copy().move(-TILE_SIZE // 2, 0)
            elif self.hit_timer:
                self.hit_timer -= 500
            else:
                self.hit_timer = None
            if self.hit is not None and self.hit.colliderect(
                    self.game.player.get_collision()):
                self.game.player.get_hit = True
                self.hit = None
            else:
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
        return pg.Rect(self.rect.x,
                       self.rect.y, TILE_SIZE, TILE_SIZE)

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
        self.gap = entity.gap
        self.max = entity.max_hp

    def update(self):
        self.rect.center = self.entity.rect.center
        self.rect.y -= self.gap
        self.image.fill(RED)
        self.image.fill(GREEN, pg.Rect(0, 0, self.entity.health_point / self.max * self.w, self.h))
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
        self.game = game
        self.image = pg.image.load(BULLET_IMG).convert()
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.direction = direction
        if self.direction == 'left':
            self.image = pg.transform.flip(self.image, True, False)

    def update(self):
        for mob in self.game.mobs:
            if self.game.camera.apply(self).colliderect(self.game.camera.apply_rect(mob.get_collision())):
                mob.get_hit = True
                self.kill()
        if self.direction == 'left':
            self.rect.x -= 2
        if self.direction == 'right':
            self.rect.x += 2


class AutoBullet(pg.sprite.Sprite):
    def __init__(self, game, x, y, player_pos):
        self.group = game.bullets
        pg.sprite.Sprite.__init__(self, self.group)
        self.game = game
        self.image = pg.image.load(AUTO_BULLET_IMG).convert()
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.bullet_speed = 1.5
        radians = math.atan2(player_pos[1] - self.rect.y, player_pos[0] - self.rect.x)
        # self.distance = int(math.hypot(player_pos[0] - self.rect.x, player_pos[1] - self.rect.y) / self.bullet_speed)

        self.dx = math.cos(radians)
        self.dy = math.sin(radians)

    def update(self):
        rect = self.game.camera.apply(self)
        if rect.colliderect(self.game.camera.apply(self.game.player)):
            self.game.player.get_hit = True
            self.kill()
        if 0 <= self.rect.x <= self.game.map.width and 0 <= self.rect.y <= self.game.map.height:
            self.rect.x += self.dx * self.bullet_speed
            self.rect.y += self.dy * self.bullet_speed
        else:
            self.kill()


class FloatingText(pg.sprite.Sprite):
    def __init__(self, game, x, y, color, size, text):
        self.group = game.floating_text
        pg.sprite.Sprite.__init__(self, self.group)
        font = pg.font.Font('img/font.ttf', size)
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, y)
        self.timer = 0

    def update(self):
        self.timer += 1
        self.rect.y -= 1
        if self.timer > 20:
            self.kill()


class BossCombo(pg.sprite.Sprite):
    def __init__(self, entity):
        self.group = entity.game.bullets
        pg.sprite.Sprite.__init__(self, self.group)
        self.game = entity.game
        self.entity = entity
        self.image = pg.Surface((0, 0))
        self.fire = pg.image.load('img/boss_combo.png')
        self.fire.set_colorkey(WHITE)
        self.fire_rect = self.fire.get_rect()
        distance = self.game.map.width
        self.img = pg.Surface((distance, 16))
        self.rect = self.img.get_rect()
        self.rect.topleft = (0, 144)
        self.img.set_colorkey(BLACK)
        for i in range(distance // 16):
            rect = self.fire_rect.move(i * 16, 0)
            self.img.blit(self.fire, rect)
        self.timer = None
        self.delay = 0

    def update(self):
        if self.timer is not None:
            if self.rect.colliderect(self.game.player.rect):
                if pg.time.get_ticks() - self.delay > 250:
                    self.game.player.get_hit = True
                    self.delay = pg.time.get_ticks()
            if pg.time.get_ticks() - self.timer > 150:
                self.kill()
        if self.entity.anim.frame >= len(self.entity.anim.animation[self.entity.anim.action]) // 1.5:
            self.image = self.img
            self.timer = pg.time.get_ticks()


class BossAttack(pg.sprite.Sprite):
    def __init__(self, entity, side):
        self.group = entity.game.bullets
        pg.sprite.Sprite.__init__(self, self.group)
        self.game = entity.game
        self.entity = entity
        self.image = pg.Surface((0, 0))
        rect = self.entity.get_collision()
        self.fire = pg.image.load('img/boss_attack.png')
        self.fire.set_colorkey(WHITE)
        self.fire_rect = self.fire.get_rect()
        if side == 'left':
            distance = rect.x
            self.img = pg.Surface((distance, 16))
            self.rect = self.img.get_rect()
            self.rect.topleft = (0, 144)
        else:
            distance = self.game.map.width - rect.x
            self.img = pg.Surface((distance, 16))
            self.rect = self.img.get_rect()
            self.rect.topleft = (rect.topright[0], 144)
        self.img.set_colorkey(BLACK)
        for i in range(distance // 16):
            rect = self.fire_rect.move(i * 16, 0)
            self.img.blit(self.fire, rect)
        self.timer = None
        self.delay = 0

    def update(self):
        if self.timer is not None:
            if self.rect.colliderect(self.game.player.rect):
                if pg.time.get_ticks() - self.delay > 250:
                    self.game.player.get_hit = True
                    self.delay = pg.time.get_ticks()
            if pg.time.get_ticks() - self.timer > 250:
                self.kill()
        if self.entity.anim.frame >= len(self.entity.anim.animation[self.entity.anim.action]) // 1.5:
            self.image = self.img
            self.timer = pg.time.get_ticks()
