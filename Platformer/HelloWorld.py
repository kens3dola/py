import csv
import sys
import pygame as pg

import random

from Platformer.entity.Entity import Entity

clock = pg.time.Clock()
pg.init()
# screen
WINDOW_SIZE = (960, 640)
pg.display.set_caption("HelloWorld")
pg.display.set_icon(pg.image.load('assets/Retro-Lines-Enemies.png'))
screen = pg.display.set_mode(WINDOW_SIZE, 0, 32)
display = pg.Surface((480, 320))

# load object images
img_source = {}


def load_animation_frame(name, action_frames):
    global img_source
    animation_frame = {}
    if name not in img_source:
        img_source[name] = {}
    for action in action_frames:
        data = action_frames[action]
        frames_data = {}
        if action not in img_source[name]:
            img_source[name][action] = {}
        frames_data = []
        for image_id in data:
            frames = data[image_id]
            img_name = 'assets/' + name + '/tile' + ('000' + str(int(image_id) - 1))[-3:] + '.png'
            if not image_id in img_source[name][action]:
                img_source[name][action][image_id] = pg.image.load(img_name)
            for frame in range(frames):
                frames_data.append(image_id)
        animation_frame[action] = frames_data
    return animation_frame


animation = load_animation_frame('player', {'idle': {'8': 7, '9': 7}, 'walk': {'1': 5, '2': 5, '3': 5, '4': 5},
                                            'attack': {'15': 7, '16': 7}, 'jump': {'22': 7, '23': 7},
                                            'hit': {'29': 14}})
enemy_animation = {
    'chicken': load_animation_frame('enemy', {'idle': {'32': 7, '33': 7, '34': 7}, 'hit': {'41': 7, '42': 7}}),
    'jelly': load_animation_frame('enemy', {'idle': {'46': 7, '47': 7, '48': 7, '49': 7}, 'hit': {'55': 7, '56': 7}}),
    'bee': load_animation_frame('enemy', {'idle': {'60': 7, '61': 7, '62': 7, '63': 7}, 'hit': {'69': 7, '70': 7}}),
    'snake': load_animation_frame('enemy', {'idle': {'74': 7, '75': 7, '76': 7, '77': 7}, 'hit': {'83': 7, '84': 7}}),
    'oneeye': load_animation_frame('enemy', {'idle': {'88': 7, '89': 7, '90': 7, '91': 7}, 'hit': {'97': 7, '98': 7}}),
    'mushroom': load_animation_frame('enemy',
                                     {'idle': {'102': 11, '103': 11, '104': 11, '105': 11, '104': 11, '103': 11,
                                               '102': 11},
                                      'hit': {'111': 7, '112': 7}}),
    'mosquito': load_animation_frame('enemy',
                                     {'idle': {'116': 7, '117': 7, '118': 7, '119': 7}, 'hit': {'125': 7, '126': 7}}),
    'scorpion': load_animation_frame('enemy',
                                     {'idle': {'130': 7, '131': 7, '132': 7, '133': 7}, 'hit': {'139': 7, '140': 7}})}

enemies = []
location = []
for i in range(6):
    loc = random.randint(0, 5) * 106 + 320
    while loc in location:
        loc = random.randint(0, 5) * 106 + 320
    location.append(loc)
num = 0
for name in enemy_animation:
    if num != len(location):
        enemies.append(Entity(location[num], 288, enemy_animation[name], img_source['enemy']))
        num += 1


def load_tile(map):
    tile_images = {}
    for i in range(len(map) - 1, -1, -1):
        for tile in map[i]:
            if tile.isnumeric() and not int(tile) == 0 and tile not in tile_images:
                img_id = '000' + str(int(tile) - 1)
                img = pg.image.load('assets/tile/tile' + img_id[-3:] + '.png')
                tile_images[tile] = img
    return tile_images


# map
file = open('assets/widermap.tmx')
game_map = [row for row in csv.reader(file)][5:25]
tile_images = load_tile(game_map)

# background
file = file = open('assets/background.tmx')
bg_map = [row for row in csv.reader(file)][5:25]
bg_images = load_tile(bg_map)

# player
rect = pg.Rect(0, 0, 16, 16)
move_r = False
move_l = False
gravity = 0
air_timer = 0
in_air = False
shooting = False
bullet_img = pg.image.load('assets/player/tile016.png')
bullets = {'l': [], 'r': []}
bullet_distance = 0
bullet_count = True
hp = 100


def collide_bullet(enemy, offside, bullet):
    true_location = pg.Rect(enemy.x - offside[0] + 12, enemy.y - offside[1], 16, 16)
    if true_location.colliderect(bullet):
        enemy.be_shot()
        return bullet
    return None


# checking collision
def collistion_list(rect, tiles):
    collide_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            collide_list.append(tile)
    return collide_list


def move(rect, movement, tiles):
    collision = {'l': False, 'u': False, 'r': False, 'd': False}
    rect.x += movement[0]
    collide_list = collistion_list(rect, tiles)
    for tile in collide_list:
        if movement[0] > 0:
            rect.right = tile.x
            collision['r'] = True
        if movement[0] < 0:
            rect.x = tile.right
            collision['l'] = True
    rect.y += movement[1]
    collide_list = collistion_list(rect, tiles)
    for tile in collide_list:
        if movement[1] > 0:
            rect.bottom = tile.y
            collision['d'] = True
        if movement[1] < 0:
            rect.top = tile.bottom
            collision['u'] = True
    return rect, collision


face_left = False

# camera
offside = [0, 0]

# animation frame
player_frame = 0
player_action = 'idle'


def change_action(action, frame, new_action):
    if not action == new_action:
        action = new_action
        frame = 0
    return action, frame


while True:
    display.fill((0, 0, 0))

    # camera offside
    if 200 <= rect.x <= 728:
        offside[0] += rect.x - offside[0] - 200
    # gravity
    gravity += 0.1

    # draw bullets
    if bullet_count:
        bullet_distance += 1
    for bullet in bullets['r']:
        bullet.x += 2
        display.blit(bullet_img, bullet)
    for bullet in bullets['l']:
        bullet.x -= 2
        display.blit(bullet_img, bullet)
    # draw background
    for i in range(len(bg_map) - 1, -1, -1):
        for j in range(len(bg_map[i]) - 1):
            if not bg_map[i][j] == '0':
                display.blit(bg_images[bg_map[i][j]], (j * 16 - offside[0] / 1.5, i * 16 - offside[1]))

    # draw map
    tile_rects = []
    for i in range(len(game_map) - 1, -1, -1):
        for j in range(len(game_map[i]) - 1):
            if not game_map[i][j] == '0':
                display.blit(tile_images[game_map[i][j]], (j * 16 - offside[0], i * 16 - offside[1]))
                tile_rects.append(pg.Rect(j * 16, i * 16, 16, 16))

    # movement
    movement = [0, 0]
    movement[1] = gravity
    if move_r:
        movement[0] += 1
    if move_l:
        movement[0] -= 1
    rect, collision = move(rect, movement, tile_rects)
    if collision['d']:
        gravity = 0
        air_timer = 0
        in_air = False
    else:
        air_timer += 1
    if collision['u']:
        gravity /= 3
    if shooting:
        player_action, player_frame = change_action(player_action, player_frame, 'attack')
    elif in_air:
        player_action, player_frame = change_action(player_action, player_frame, 'jump')
    elif not movement[0] == 0:
        player_action, player_frame = change_action(player_action, player_frame, 'walk')
    else:
        player_action, player_frame = change_action(player_action, player_frame, 'idle')

    rico_bullet_l = []
    rico_bullet_r = []
    for enemy in enemies:
        enemy.render(offside, display)
        enemy.update(rect)
        hp = enemy.attack(rect, hp)
        for bullet in bullets['l']:
            hit_bullet = collide_bullet(enemy, offside, bullet)
            if hit_bullet:
                rico_bullet_l.append(hit_bullet)
        for bullet in bullets['r']:
            hit_bullet = collide_bullet(enemy, offside, bullet)
            if hit_bullet:
                rico_bullet_r.append(hit_bullet)
    for b in rico_bullet_l:
        try:
            bullets['l'].remove(b)
        except:
            pass
    for b in rico_bullet_r:
        try:
            bullets['r'].remove(b)
        except:
            pass

    # draw player
    player_image_id = animation[player_action][player_frame]
    player_img = img_source['player'][player_action][player_image_id]
    if (rect.y > WINDOW_SIZE[1]): rect = pg.Rect(0, 0, 16, 16)
    display.blit(pg.transform.flip(player_img, face_left, False), (rect.x - offside[0], rect.y - offside[1]))

    # draw hp
    pg.draw.rect(display, (255, 255, 255), pg.Rect(5, 5, 100 / 2, 8))
    display.fill((252, 3, 3), pg.Rect(5, 5, hp / 2, 8))

    # increase frame
    player_frame += 1
    if player_frame >= len(animation[player_action]):
        player_frame = 0
    # event
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT:
                move_r = True
                face_left = False
            if event.key == pg.K_LEFT:
                move_l = True
                face_left = True
            if event.key == pg.K_UP and air_timer <= 40:
                gravity = -2.5
                in_air = True
            if event.key == pg.K_SPACE:
                shooting = True
                if bullet_distance > 35:
                    if face_left:
                        bullets['l'].append(pg.Rect(rect.x - offside[0], rect.y, 16, 16))
                    else:
                        bullets['r'].append(pg.Rect(rect.x - offside[0], rect.y, 16, 16))
                    bullet_distance = 0
                bullet_count = True
        if event.type == pg.KEYUP:
            if event.key == pg.K_RIGHT:
                move_r = False
            if event.key == pg.K_LEFT:
                move_l = False
            if event.key == pg.K_SPACE:
                shooting = False
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

    screen.blit(pg.transform.scale(display, WINDOW_SIZE), (0, 0))
    pg.display.update()
    clock.tick(120)
