#!/usr/bin/python3.4
# Setup Python ----------------------------------------------- #
import pygame, sys, random, time, webbrowser, os, text
from datetime import datetime
import entities as e
import rotation as rot

# Setup pygame/window ---------------------------------------- #
mainClock = pygame.time.Clock()
from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.display.set_caption('Whirling Blades')
WINDOWWIDTH = 600
WINDOWHEIGHT = 400
screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
display = pygame.Surface((300, 200))


# FPS -------------------------------------------------------- #
def ms():
    return int(round(time.time() * 1000))


def get_ms():
    global start_time
    return int(round(time.time() * 1000)) - start_time


global start_time
start_time = ms()


# Font ------------------------------------------------------- #
def get_text_width(text, spacing):
    global font_dat
    width = 0
    for char in text:
        if char in font_dat:
            width += font_dat[char][0] + spacing
        elif char == ' ':
            width += font_dat['A'][0] + spacing
    return width


global font_dat
font_dat = {'A': [3], 'B': [3], 'C': [3], 'D': [3], 'E': [3], 'F': [3], 'G': [3], 'H': [3], 'I': [3], 'J': [3],
            'K': [3], 'L': [3], 'M': [5], 'N': [3], 'O': [3], 'P': [3], 'Q': [3], 'R': [3], 'S': [3], 'T': [3],
            'U': [3], 'V': [3], 'W': [5], 'X': [3], 'Y': [3], 'Z': [3],
            'a': [3], 'b': [3], 'c': [3], 'd': [3], 'e': [3], 'f': [3], 'g': [3], 'h': [3], 'i': [1], 'j': [2],
            'k': [3], 'l': [3], 'm': [5], 'n': [3], 'o': [3], 'p': [3], 'q': [3], 'r': [2], 's': [3], 't': [3],
            'u': [3], 'v': [3], 'w': [5], 'x': [3], 'y': [3], 'z': [3],
            '.': [1], '-': [3], ',': [2], ':': [1], '+': [3], '\'': [1], '!': [1], '?': [3],
            '0': [3], '1': [3], '2': [3], '3': [3], '4': [3], '5': [3], '6': [3], '7': [3], '8': [3], '9': [3],
            '(': [2], ')': [2], '/': [3], '_': [5], '=': [3], '\\': [3], '[': [2], ']': [2], '*': [3], '"': [3],
            '<': [3], '>': [3], ';': [1]}
font_0 = text.generate_font('data/font/small_font.png', font_dat, 5, 8, (16, 30, 41))
font_1 = text.generate_font('data/font/small_font.png', font_dat, 5, 8, (248, 248, 248))


# Functions -------------------------------------------------- #
def reduce(num, amount):
    if num >= amount:
        num -= amount
    elif num <= -amount:
        num += amount
    else:
        num = 0
    return num


def loc(x, y):
    return str(x) + ';' + str(y)


def ordered_render(img, pos, z=None, secondary_sort=0):
    x = pos[0]
    y = pos[1]
    global for_render, image_cache
    if z == None:
        z = y + img.get_height()
    image_cache.append(img)
    for_render.append([z, secondary_sort, x, y, len(image_cache) - 1])


def get_nearby_tiles(pos, tiles):
    global decor
    nearby_tiles = []
    pos = [int(pos[0] / 32), int(pos[1] / 32)]
    for y in range(5):
        for x in range(5):
            pos_str = loc(pos[0] + x - 2, pos[1] + y - 2)
            if pos_str not in tiles:
                nearby_tiles.append([(pos[0] + x - 2) * 32, (pos[1] + y - 2) * 32, 32, 32])
            elif tiles[pos_str][3] != 0:
                nearby_tiles.append([(pos[0] + x - 2) * 32, (pos[1] + y - 2) * 32, 32, 32])
            elif pos_str in decor:
                nearby_tiles.append([(pos[0] + x - 2) * 32, (pos[1] + y - 2) * 32, 32, 32])
    return nearby_tiles


def cap(num, amount):
    if num > amount:
        num = amount
    if num < -amount:
        num = -amount
    return num


def add_img_particles(img, base_pos, blood=True, duration=40):
    global particles
    width = img.get_width()
    height = img.get_height()
    for y in range(height):
        for x in range(width):
            color = img.get_at((x, y))
            if color != (255, 255, 255, 255):
                # color, x, y, x_momentum, y_momentum, duration
                if blood == True:
                    particles.append([(169, 59, 59), x + base_pos[0], y + base_pos[1], random.randint(0, 20) / 10 - 1,
                                      random.randint(0, 20) / 10 - 1, random.randint(10, 30)])
                particles.append(
                    [color, x + base_pos[0], y + base_pos[1], 0, 0, random.randint(duration, int(duration * 1.5))])


def flip(img, boolean):
    return pygame.transform.flip(img, boolean, False).copy()


def add_item(item):
    global inventory
    for slot in inventory:
        if slot[0] == item:
            slot[1] += 1
            return None
    for slot in inventory:
        if slot[0] == None:
            slot[0] = item
            slot[1] = 1
            return None


# Audio ------------------------------------------------------ #
def load_snd(name):
    return pygame.mixer.Sound('data/sfx/' + name + '.wav')


hurt_s = load_snd('hurt')
attack_s = load_snd('attack')
dash_s = load_snd('dash')
explosion_s = load_snd('explosion')
hit_s = load_snd('hit')
hit_decor_s = load_snd('hit_decor')
attack_s.set_volume(0.5)
dash_s.set_volume(0.3)

pygame.mixer.music.load('data/music/main.wav')


# Images ----------------------------------------------------- #
def load_img(path):
    img = pygame.image.load('data/images/' + path + '.png').convert()
    img.set_colorkey((255, 255, 255))
    return img


bars_img = load_img('bars')

tile_images = {'grass': load_img('tiles/grass'), 'muck': load_img('tiles/muck')}
weapons = {'sword_0': load_img('weapons/sword_0'), 'sword_1': load_img('weapons/sword_1'),
           'sword_2': load_img('weapons/sword_2'), 'sword_3': load_img('weapons/sword_3')}
# ID: img, offset y
decor_images = {'bush': [load_img('decor/bush'), -2], 'blueberries': [load_img('decor/blueberries'), -2],
                'tree': [load_img('decor/tree'), -18], 'apples': [load_img('decor/apples'), -18]}
item_images = {'blueberries': load_img('items/blueberries'), 'apples': load_img('items/apples'),
               'seeds': load_img('items/seeds'), 'gel': load_img('items/gel')}
slot_img = load_img('slot')
shot_img = load_img('shot')
weapon_slot = load_img('weapon_slot')
weapon_items = {'sword_0': load_img('weapon_items/sword_0'), 'sword_1': load_img('weapon_items/sword_1'),
                'sword_2': load_img('weapon_items/sword_2'), 'sword_3': load_img('weapon_items/sword_3')}
controls_img = load_img('controls')
cloud_images = {'cloud_0': load_img('cloud_0'), 'cloud_1': load_img('cloud_1'), 'cloud_2': load_img('cloud_2'),
                'cloud_3': load_img('cloud_3')}

fly_stand_f = load_img('entities/fly/stand_f')
fly_stand_b = load_img('entities/fly/stand_b')
fly_fly_f = load_img('entities/fly/fly_f')
fly_fly_b = load_img('entities/fly/fly_b')
# Animations ------------------------------------------------- #
player_walk_f = e.animation_sequence([[0, 3], [1, 2], [2, 3], [1, 2]], 'data/images/entities/player/walk_f_')
player_walk_b = e.animation_sequence([[0, 3], [1, 2], [2, 3], [1, 2]], 'data/images/entities/player/walk_b_')
player_stand_f = load_img('entities/player/stand_f')
player_stand_b = load_img('entities/player/stand_b')

dust_anim = e.animation_sequence([[0, 4], [1, 3], [2, 3], [3, 4], [4, 3], [5, 3], [6, 3], [7, 3], [8, 5]],
                                 'data/images/misc_animations/dust_')

tank_main_f = e.animation_sequence([[0, 120], [1, 5], [2, 7], [1, 5]], 'data/images/entities/tank/main_f_')
tank_main_b = e.animation_sequence([[0, 120], [1, 5], [2, 7], [1, 5]], 'data/images/entities/tank/main_b_')
stomper_stomp = e.animation_sequence([[0, 80], [1, 4], [2, 4], [3, 2], [4, 2], [5, 2], [6, 2]],
                                     'data/images/entities/stomper/stomp_')

sword_0_gfx = e.animation_sequence(
    [[0, 1], [1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [7, 1], [8, 1], [9, 1], [10, 1], [11, 1], [12, 1], [13, 1],
     [14, 1], [15, 1], [16, 1], [17, 1], [18, 1], [19, 1], [20, 1]], 'data/images/weapon_effects/sword_0_')
sword_1_gfx = e.animation_sequence(
    [[0, 1], [1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [7, 1], [8, 1], [9, 1], [10, 1], [11, 1], [12, 1], [13, 1],
     [14, 1], [15, 1], [16, 1], [17, 1], [18, 1], [19, 1], [20, 1]], 'data/images/weapon_effects/sword_1_')
sword_2_gfx = e.animation_sequence(
    [[0, 1], [1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [7, 1], [8, 1], [9, 1], [10, 1], [11, 1], [12, 1], [13, 1],
     [14, 1], [15, 1], [16, 1], [17, 1], [18, 1], [19, 1], [20, 1]], 'data/images/weapon_effects/sword_2_')
sword_3_gfx = e.animation_sequence(
    [[0, 1], [1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [7, 1], [8, 1], [9, 1], [10, 1], [11, 1], [12, 1], [13, 1],
     [14, 1], [15, 1], [16, 1], [17, 1], [18, 1], [19, 1], [20, 1]], 'data/images/weapon_effects/sword_3_')

explosion_anim = e.animation_sequence(
    [[0, 4], [1, 4], [2, 4], [3, 4], [4, 6], [5, 6], [6, 6], [7, 4], [8, 4], [9, 4], [10, 4], [11, 4], [12, 4], [13, 4],
     [14, 4]], 'data/images/misc_animations/explosion_')

weapon_gfx = {'sword_0': sword_0_gfx, 'sword_1': sword_1_gfx, 'sword_2': sword_2_gfx, 'sword_3': sword_3_gfx}


def gen_id(name, frame):  # generate IDs for weapon GFX frames
    return 'data/images/weapon_effects/' + name + '_' + str(frame)


# Font ------------------------------------------------------- #
# Variables -------------------------------------------------- #
# type, x, y, z
tiles = {'0;0': ['grass', 0, 0, 0], '0;1': ['grass', 0, 1, 0], '1;0': ['grass', 1, 0, 0], '1;1': ['grass', 1, 1, 0]}
global decor
decor = {}
scroll_x = -100
scroll_y = -50
SKY = (146, 244, 255)
directions = [0, 0, 0, 0]
dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]]
new_tile_timer = 0

player = e.entity(0, 0, 20, 20)
player.set_animation_tags(['loop'])
player.animation = player_walk_f

player_dir = 'down'

player_knockback = [0, 0]

current_weapon = 'sword_0'

attack_sizes = {'sword_0': 104, 'sword_1': 124, 'sword_2': 140, 'sword_3': 144}
attack_powers = {'sword_0': 4, 'sword_1': 5, 'sword_2': 7, 'sword_3': 7}
attack_knockbacks = {'sword_0': 8, 'sword_1': 12, 'sword_2': 16, 'sword_3': 16}
enemy_knockbacks = {'fly': 4, 'stomper': 6, 'tank': 14}
enemy_damages = {'fly': 3, 'stomper': 5, 'tank': 10}
knockback_multipliers = {'fly': 1, 'stomper': 0.25, 'tank': 0.125}
enemy_health = {'fly': 10, 'stomper': 12, 'tank': 24}

attack_timer = -1  # goes to 360 for the degrees of the rotation
attack_base = 0
dash_timer = -1
dash_start = [0, 0]

health = 100
energy = 50

rate_x = 0.5
rate_y = 0.5

# the map is handled as a normal 2D map where the tiles are 32x32
# the player is a 20x20 square

last_frame = get_ms()

alerts = []

global for_render
for_render = []
global image_cache
image_cache = []

enemies = []
enemy_types = ['fly', 'fly', 'fly', 'stomper', 'fly', 'fly', 'stomper', 'fly', 'fly', 'tank']
decor_types = ['bush', 'bush', 'bush', 'bush', 'tree', 'blueberries', 'blueberries', 'tree', 'tree', 'apples']
cloud_types = ['cloud_0', 'cloud_0', 'cloud_1', 'cloud_0', 'cloud_0', 'cloud_1', 'cloud_2']

global particles
particles = []

screen_shake = 0

new_game = 180

hurt = 0

lock_mouse = False

time_alive = 0

explosions = []

projectiles = []

dust = []

paused = False

minutes = 0

remove_tiles = []

next_enemy = None

# type, x, y, scroll_rate, speed
clouds = []
for i in range(10):
    depth = random.randint(0, 5) / 10 + 0.25
    clouds.append([random.choice(cloud_types), random.randint(-44, 290) + scroll_x * depth,
                   random.randint(0, 200) + scroll_y * depth, depth, random.randint(4, 10) / 20])

global inventory
inventory = [[None, 0, -30], [None, 0, -30], [None, 0, -30], [None, 0, -30]]

pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.65)
# Loop ------------------------------------------------------- #
while True:
    # Background --------------------------------------------- #
    display.fill(SKY)
    # Clouds ------------------------------------------------- #
    if random.randint(1, 80) == 1:
        depth = random.randint(0, 5) / 10 + 0.25
        t = random.choice(cloud_types)
        if random.randint(1, 1000) == 1:
            t = 'cloud_3'
        clouds.append(
            [t, -44 + scroll_x * depth, random.randint(0, 200) + scroll_y * depth, depth, random.randint(4, 10) / 20])
    n = 0
    for cloud in clouds:
        cloud[1] += cloud[4]
        display.blit(cloud_images[cloud[0]], (cloud[1] - scroll_x * cloud[3], cloud[2] - scroll_y * cloud[3]))
        if cloud[1] - scroll_x * cloud[3] > 320:
            clouds.pop(n)
            n -= 1
        n += 1
    if time_alive == 1400:
        next_enemy = 'tank'
    # Background Logic --------------------------------------- #
    if new_game != 0:
        new_game -= 1
        new_tile_rate = 2
    else:
        new_tile_rate = 13
    if minutes > 8:
        new_tile_rate = 8
    if new_tile_timer >= 0:
        new_tile_timer += 1
    if new_tile_timer >= new_tile_rate:
        keys = []
        for key in tiles.keys():  # get key list
            keys.append(key)
        not_placed = True
        while not_placed:  # don't stop until a tile is placed
            key = random.choice(keys)  # pick a random tile
            open_spots = []
            for direction in dirs:  # check all directions for the tile
                x = tiles[key][1] + direction[0]
                y = tiles[key][2] + direction[1]
                if loc(x, y) not in tiles:
                    open_spots.append([x, y])  # add open tile
            if open_spots != []:
                spot = random.choice(open_spots)  # pick open tile
                tiles[loc(spot[0], spot[1])] = ['grass', spot[0], spot[1], 200]  # place tile
                if random.randint(1, int((0.7 / time_alive + 1 / 2000) * 5000)) == 1:
                    if new_game == 0:
                        # type, entity, knockback, health, invulnerable
                        t = random.choice(enemy_types)
                        if t == 'tank':
                            if time_alive < 2000:
                                t = 'fly'
                        if next_enemy != None:
                            t = next_enemy
                            next_enemy = None
                        enemies.append(
                            [t, e.entity(spot[0] * 32 + 6, spot[1] * 32 + 6, 20, 20), [0, 0], enemy_health[t], 0])
                elif random.randint(1, 3) == 1:
                    decor[loc(spot[0], spot[1])] = [random.choice(decor_types), spot[0], spot[1]]
                not_placed = False
        new_tile_timer = 0
    # Handle Player ------------------------------------------ #
    player_standing = False

    if attack_timer != -1:
        attack_timer += 45
        if attack_timer >= 900:
            attack_timer = -1

    while abs(player_knockback[0]) + abs(player_knockback[1]) > 30:
        if abs(player_knockback[0]) > abs(player_knockback[1]):
            while abs(player_knockback[0]) > 15:  # knockback cap
                if player_knockback[1] == 0:
                    player_knockback[1] = 0.1
                player_knockback[1] -= 1 / abs(player_knockback[0]) * player_knockback[1] / abs(player_knockback[1])
                player_knockback[0] = reduce(player_knockback[0], 1)
        else:
            while abs(player_knockback[1]) > 15:  # knockback cap
                if player_knockback[0] == 0:
                    player_knockback[0] = 0.1
                player_knockback[0] -= 1 / abs(player_knockback[1]) * player_knockback[0] / abs(player_knockback[0])
                player_knockback[1] = reduce(player_knockback[1], 1)

    movement = [player_knockback[0], player_knockback[1]]
    player_knockback[0] = reduce(player_knockback[0], 0.75)
    player_knockback[1] = reduce(player_knockback[1], 0.75)
    speed = 3
    if dash_timer != -1:
        dash_timer += 1
        if dash_timer == 10:
            dash_timer = -1
        speed = 18
        if current_weapon == 'sword_2':
            speed = 24
        elif current_weapon == 'sword_3':
            speed = 28

    # slower on muck
    pos = loc(int(round((player.x - 0.5) / 32, 0)), int(round((player.y - 0.5) / 32, 0)))
    try:
        if tiles[pos][0] == 'muck':
            speed /= 3
            for item in inventory:
                if item[0] == 'seeds':
                    item[1] -= 1
                    if item[1] <= 0:
                        item[0] = None
                    alerts.append(['-seeds', 0])
                    tiles[pos][0] = 'grass'
    except KeyError:
        pass

    movement[1] += rate_y * speed * 1.2 - rate_x * speed
    movement[0] += rate_y * speed * 1.2 + rate_x * speed

    if rate_y > 0:
        player.animation = player_walk_f
        player_dir = 'down'
        player.change_frame(1)
    elif rate_y < 0:
        player.animation = player_walk_b
        player_dir = 'up'
        player.change_frame(1)
    else:
        player.animation = None
        player_standing = True
        if player_dir == 'down':
            player.set_image(player_stand_f)
        else:
            player.set_image(player_stand_b)
    if rate_x > 0:
        player.set_flip(False)
    elif rate_x < 0:
        player.set_flip(True)

    if attack_timer != -1:
        if (weapon_rot % 360 < 90) or (weapon_rot % 360 > 270):
            player.set_flip(False)
        else:
            player.set_flip(True)
        if weapon_rot % 360 < 180:
            player.animation = player_walk_f
            player_dir = 'down'
        else:
            player.animation = player_walk_b
            player_dir = 'up'

    nearby_collidables = []
    player_loc = [int(player.x / 32), int(player.y / 32)]
    for y in range(7):
        for x in range(7):
            pos_raw = [x + player_loc[0] - 3, y + player_loc[1] - 3]
            pos = loc(pos_raw[0], pos_raw[1])
            if pos not in tiles:
                nearby_collidables.append([pos_raw[0] * 32, pos_raw[1] * 32, 32, 32])
            elif tiles[pos][3] > 0:
                nearby_collidables.append([pos_raw[0] * 32, pos_raw[1] * 32, 32, 32])
            elif pos in decor:
                nearby_collidables.append([pos_raw[0] * 32, pos_raw[1] * 32, 32, 32])
    movement[0] = cap(movement[0], 24)
    movement[1] = cap(movement[1], 24)
    player.move(movement, nearby_collidables)
    player_img = player.get_current_img()
    # Handle Attacks ----------------------------------------- #
    hit_enemy = False
    hit_decor = False
    been_hurt = False
    attackR = pygame.Rect(player.x + 10 - int(attack_sizes[current_weapon] / 2),
                          player.y + 10 - int(attack_sizes[current_weapon] / 2), attack_sizes[current_weapon],
                          attack_sizes[current_weapon])
    n = 0
    for projectile in projectiles:
        projectileR = pygame.Rect(projectile[0], projectile[1], 20, 20)
        if projectileR.colliderect(attackR):
            render_pos = (int(projectile[0] / 32 * 14 - projectile[1] / 32 * 14),
                          int(projectile[0] / 32 * 7 + projectile[1] / 32 * 7))
            add_img_particles(shot_img, render_pos, False, 20)
            projectiles.pop(n)
            hit_decor = True
            n -= 1
        n += 1
    for enemy in enemies:
        if player.obj.rect.colliderect(enemy[1].obj.rect):
            if dash_timer == -1:
                health -= enemy_damages[enemy[0]]
                hurt += enemy_damages[enemy[0]] * 5
                e_dis_x = enemy[1].x - player.x
                e_dis_y = enemy[1].y - player.y
                if (e_dis_x == 0) and (e_dis_y == 0):
                    e_dis_x = 1
                    e_dis_y = 1
                e_rate_x = e_dis_x / (abs(e_dis_x) + abs(e_dis_y))
                e_rate_y = e_dis_y / (abs(e_dis_x) + abs(e_dis_y))
                player_knockback[0] -= e_rate_x * enemy_knockbacks[enemy[0]] * 4
                player_knockback[1] -= e_rate_y * enemy_knockbacks[enemy[0]] * 4
                been_hurt = True
        if attack_timer != -1:
            if attackR.colliderect(enemy[1].obj.rect):
                if enemy[4] == 0:
                    try:
                        tile_z = tiles[loc(int((enemy[1].x - 6) / 32), int((enemy[1].y - 6) / 32))][3]
                    except KeyError:
                        tile_z = 0
                    if tile_z == 0:
                        enemy[4] = 10
                        enemy[3] -= attack_powers[current_weapon]
                        e_dis_x = enemy[1].x - player.x
                        e_dis_y = enemy[1].y - player.y
                        if (e_dis_x == 0) and (e_dis_y == 0):
                            e_dis_x = 1
                            e_dis_y = 1
                        e_rate_x = e_dis_x / (abs(e_dis_x) + abs(e_dis_y))
                        e_rate_y = e_dis_y / (abs(e_dis_x) + abs(e_dis_y))
                        enemy[2][0] += e_rate_x * attack_knockbacks[current_weapon] * knockback_multipliers[enemy[0]]
                        enemy[2][1] += e_rate_y * attack_knockbacks[current_weapon] * knockback_multipliers[enemy[0]]
                        screen_shake += int(enemy_knockbacks[enemy[0]])
                        player_knockback[0] -= e_rate_x * enemy_knockbacks[enemy[0]]
                        player_knockback[1] -= e_rate_y * enemy_knockbacks[enemy[0]]
                        hit_enemy = True
    if hit_enemy:
        hit_s.play()
    if been_hurt:
        hurt_s.play()
    # Remove Tiles ------------------------------------------- #
    n = 0
    for tile in remove_tiles:
        try:
            if tiles[tile][3] == 0:
                tiles[tile][3] = 1
            tiles[tile][3] -= (0 - tiles[tile][3]) / 10
        except KeyError:
            remove_tiles.pop(n)
            n -= 1
        n += 1
    # Render Tiles ------------------------------------------- #
    temp_scroll_x = scroll_x + 5
    temp_scroll_y = scroll_y - 93
    start_pos = [int(temp_scroll_x / 28) + int(temp_scroll_y / 14) + 4,
                 int(temp_scroll_y / 14) - int(temp_scroll_x / 28) - 4]
    render_box_size = 30
    render_box = {}
    remove_list = []
    for y in range(render_box_size):
        for x in range(render_box_size):
            try:
                key = loc(x + start_pos[0], y + start_pos[1])
                render_box[key] = tiles[key].copy()
                if tiles[key][3] > 0:
                    if key not in remove_tiles:
                        tiles[key][3] -= tiles[key][3] / 10
                    if tiles[key][3] < 1:
                        tiles[key][3] = 0
                    if tiles[key][3] > 250:
                        remove_list.append(key)
            except KeyError:
                pass
    for i in range(render_box_size * 2 - 1):  # handle all the diagonals
        for i2 in range(render_box_size):  # iterate through the tiles within the diagonals
            pos = [i - i2, i2]
            try:
                # print(render_box[loc(pos[0]+start_pos[0],pos[1]+start_pos[1])])
                tile = render_box[loc(pos[0] + start_pos[0], pos[1] + start_pos[1])]
                display.blit(tile_images[tile[0]], (
                tile[1] * 14 - tile[2] * 14 - int(scroll_x), tile[1] * 7 + tile[2] * 7 - int(scroll_y) + int(tile[3])))
            except KeyError:
                pass
    for tile in remove_list:
        del tiles[tile]
        if tile in render_box:
            del render_box[tile]
    # Handle Decor ------------------------------------------- #
    remove_list = []
    for obj in decor:
        x = decor[obj][1]
        y = decor[obj][2]
        try:
            z = render_box[obj][3]
        except:
            z = -1
        if z != -1:
            render_pos = (
            int(x * 14 - y * 14) - scroll_x, int(x * 7 + y * 7) + decor_images[decor[obj][0]][1] - scroll_y - z)
            ordered_render(decor_images[decor[obj][0]][0], render_pos)
            objR = pygame.Rect(x * 32, y * 32, 32, 32)
            if attack_timer != -1:
                if attackR.colliderect(objR):
                    if tiles[obj][3] == 0:
                        if decor[obj][0] == 'blueberries':
                            add_item('blueberries')
                            alerts.append(['+blueberries', 0])
                        if decor[obj][0] == 'apples':
                            add_item('apples')
                            alerts.append(['+apples', 0])
                        if random.randint(1, 8) == 1:
                            if current_weapon == 'sword_3':
                                for i in range(6):
                                    add_item('seeds')
                                alerts.append(['+6 seeds', 0])
                            elif current_weapon == 'sword_2':
                                for i in range(4):
                                    add_item('seeds')
                                alerts.append(['+4 seeds', 0])
                            else:
                                for i in range(2):
                                    add_item('seeds')
                                alerts.append(['+2 seeds', 0])
                        add_img_particles(decor_images[decor[obj][0]][0],
                                          (render_pos[0] + scroll_x, render_pos[1] + scroll_y), False, 20)
                        remove_list.append(obj)
                        hit_decor = True
    for obj in remove_list:
        del decor[obj]
    if hit_decor:
        hit_decor_s.play()
    # Particles ---------------------------------------------- #
    n = 0
    for particle in particles:
        # color, x, y, x_momentum, y_momentum, duration
        display.set_at((int(particle[1] - scroll_x), int(particle[2] - scroll_y)), particle[0])
        particle[1] += particle[3]
        particle[2] += particle[4]
        particle[5] -= 1
        if particle[5] < 25:
            if (particle[3] == 0) and (particle[4] == 0):
                particle[3] = random.randint(0, 20) / 10 - 1
                particle[4] = random.randint(0, 20) / 10 - 1
        if particle[5] <= 0:
            particles.pop(n)
            n -= 1
        n += 1
    # Explosions --------------------------------------------- #
    n = 0
    for explosion in explosions:
        if explosion[1] == 0:
            explosion[0].set_animation(explosion_anim)
        explosion_img = explosion[0].get_current_img()
        render_pos = (int(explosion[0].x / 32 * 14 - explosion[0].y / 32 * 14) - scroll_x,
                      int(explosion[0].x / 32 * 7 + explosion[0].y / 32 * 7) - 17 - scroll_y)
        ordered_render(explosion_img, render_pos)
        explosion[0].change_frame(1)
        explosion[1] += 1
        if explosion[1] == 16:
            try:
                pos = loc(int(explosion[0].x / 32), int(explosion[0].y / 32))
                tiles[pos][0] = 'muck'
            except KeyError:
                pass
        if explosion[1] == 38:
            explosion_s.play()
        if explosion[1] == 42:
            if explosion[0].obj.rect.colliderect(player.obj.rect):
                e_dis_x = explosion[0].x - player.x
                e_dis_y = explosion[0].y - player.y
                if (e_dis_x == 0) and (e_dis_y == 0):
                    e_dis_x = 1
                    e_dis_y = 1
                e_rate_x = e_dis_x / (abs(e_dis_x) + abs(e_dis_y))
                e_rate_y = e_dis_y / (abs(e_dis_x) + abs(e_dis_y))
                player_knockback[0] -= e_rate_x * 12
                player_knockback[1] -= e_rate_y * 12
                health -= 15
                hurt += 15 * 5
        if explosion[1] == 66:
            explosions.pop(n)
            n -= 1
        n += 1
    # Enemies ------------------------------------------------ #
    n = 0
    for enemy in enemies:
        enemy_img = None
        enemy_movement = [enemy[2][0], enemy[2][1]]  # apply base momentum
        enemy[2][0] = reduce(enemy[2][0], 0.5)
        enemy[2][1] = reduce(enemy[2][1], 0.5)
        if enemy[4] > 0:
            enemy[4] -= 1
        if enemy[0] in ['fly', 'tank']:
            if len(enemy) == 5:
                enemy.append(0)  # add the AI state
                enemy.append(['f', False])  # direction
                if enemy[0] == 'tank':
                    enemy[1].set_animation_tags(['loop'])
            try:
                tile_z = render_box[loc(int((enemy[1].x - 6) / 32), int((enemy[1].y - 6) / 32))][3]
            except KeyError:
                if loc(int((enemy[1].x - 6) / 32), int((enemy[1].y - 6) / 32)) in tiles:
                    tile_z = -1
                else:
                    tile_z = 0
            if enemy[0] == 'fly':
                enemy_img = fly_stand_f.copy()
                enemy_offset = [7, -7 - tile_z]
            if enemy[0] == 'tank':
                enemy_offset = [0, -14 - tile_z]
                enemy[1].animation = tank_main_f
                enemy_img = enemy[1].get_current_img()
            if tile_z == 0:
                enemy[5] += 1
            if enemy[5] == 30:
                enemy[5] = 0 - random.randint(15, 35)
            if ((enemy[5] < 0) or (enemy[0] == 'tank')) and (tile_z == 0):
                # ai
                e_dis_x = player.x - enemy[1].x
                e_dis_y = player.y - enemy[1].y
                if (e_dis_x == 0) and (e_dis_y == 0):
                    e_dis_x = 1
                    e_dis_y = 1
                e_rate_x = e_dis_x / (abs(e_dis_x) + abs(e_dis_y))
                e_rate_y = e_dis_y / (abs(e_dis_x) + abs(e_dis_y))
                if enemy[0] == 'fly':
                    speed = 5
                if enemy[0] == 'tank':
                    speed = 1.5
                enemy_movement[0] += e_rate_x * speed
                enemy_movement[1] += e_rate_y * speed * 1.2
                if e_rate_x > e_rate_y * 1.2:
                    if e_rate_x > 0:
                        enemy[6][1] = False
                        enemy[6][0] = 'f'
                    elif e_rate_x < 0:
                        enemy[6][1] = False
                        enemy[6][0] = 'b'
                else:
                    if e_rate_y > 0:
                        enemy[6][1] = True
                        enemy[6][0] = 'f'
                    elif e_rate_y < 0:
                        enemy[6][1] = True
                        enemy[6][0] = 'b'
                if enemy[0] == 'fly':
                    if enemy[6][0] == 'f':
                        enemy_img = flip(fly_fly_f, enemy[6][1]).copy()
                    if enemy[6][0] == 'b':
                        enemy_img = flip(fly_fly_b, enemy[6][1]).copy()
                elif enemy[0] == 'tank':
                    if enemy[1].animation_frame == 132:
                        if len(projectiles) < 40:
                            projectiles.append([enemy[1].x + 5, enemy[1].y - 5, e_rate_x, e_rate_y, 0])
                        damageR = pygame.Rect(enemy[1].x + 14 - 32, enemy[1].y + 11 - 32, 64, 64)
                        if damageR.colliderect(player):
                            health -= 5
                            hurt += 25
                            e_dis_x = enemy[1].x - player.x
                            e_dis_y = enemy[1].y - player.y
                            if (e_dis_x == 0) and (e_dis_y == 0):
                                e_dis_x = 1
                                e_dis_y = 1
                            e_rate_x = e_dis_x / (abs(e_dis_x) + abs(e_dis_y))
                            e_rate_y = e_dis_y / (abs(e_dis_x) + abs(e_dis_y))
                            player_knockback[0] -= e_rate_x * enemy_knockbacks[enemy[0]] * 8
                            player_knockback[1] -= e_rate_y * enemy_knockbacks[enemy[0]] * 8
                    if enemy[6][0] == 'f':
                        enemy[1].animation = tank_main_f
                    if enemy[6][0] == 'b':
                        enemy[1].animation = tank_main_b
                    enemy[1].change_frame(1)
                    enemy_img = enemy[1].get_current_img()
            elif enemy[0] == 'fly':
                if enemy[6][0] == 'f':
                    enemy_img = flip(fly_stand_f, enemy[6][1]).copy()
                if enemy[6][0] == 'b':
                    enemy_img = flip(fly_stand_b, enemy[6][1]).copy()
        if enemy[0] == 'stomper':
            if len(enemy) == 5:
                enemy[1].animation = stomper_stomp
                enemy[1].set_animation_tags(['loop'])
            enemy_img = enemy[1].get_current_img()
            enemy[1].change_frame(1)
            try:
                tile_z = render_box[loc(int((enemy[1].x - 6) / 32), int((enemy[1].y - 6) / 32))][3]
            except KeyError:
                if loc(int((enemy[1].x - 6) / 32), int((enemy[1].y - 6) / 32)) in tiles:
                    tile_z = -1
                else:
                    tile_z = 0
            if enemy[1].animation_frame == 86:
                for attampt in range(10):
                    try:
                        pos_raw = [int(player.x / 32) + random.randint(0, 3) - 1,
                                   int(player.y / 32) + random.randint(0, 3) - 1]
                        pos = loc(pos_raw[0], pos_raw[1])
                        if tiles[pos][0] == 'grass':
                            if tiles[pos][3] == 0:
                                explosions.append([e.entity(pos_raw[0] * 32, pos_raw[1] * 32, 32, 32), 0])
                                break
                    except KeyError:
                        pass
            enemy_offset = [5, -15 - tile_z]
        if enemy[4] > 0:
            if enemy[3] > 0:
                red_surf = pygame.Surface((enemy_img.get_width(), enemy_img.get_height()))
                red_surf.fill((100, 0, 0))
                red_surf.set_alpha(400 - enemy[4] * 20)
                enemy_img.blit(red_surf, (0, 0), special_flags=BLEND_ADD)
        enemy[1].move(enemy_movement, get_nearby_tiles((enemy[1].x, enemy[1].y), tiles))
        render_pos = (int(enemy[1].x / 32 * 14 - enemy[1].y / 32 * 14) + enemy_offset[0] - scroll_x,
                      int(enemy[1].x / 32 * 7 + enemy[1].y / 32 * 7) + enemy_offset[1] - scroll_y)
        if enemy[0] == 'tank':
            if tile_z == 0:
                if random.randint(1, 3) == 1:
                    dust.append([e.entity(render_pos[0] + scroll_x + 14, render_pos[1] + scroll_y + 22, 2, 2),
                                 random.randint(0, 20) / 20 - 0.5, random.randint(0, 20) / 20 - 0.5, 0])
        if enemy[3] <= 0:
            if enemy[0] == 'fly':
                tile_str = str(int(round(enemy[1].x / 32, 0))) + ';' + str(int(round(enemy[1].y / 32, 0)))
                if tile_str in tiles:
                    if tile_str not in decor:
                        tileR = pygame.Rect(tiles[tile_str][1] * 32, tiles[tile_str][2] * 32, 32, 32)
                        collided = False
                        for projectile in projectiles:
                            projectileR = pygame.Rect(projectile[0], projectile[1], 20, 20)
                            if projectileR.colliderect(tileR):
                                collided = True
                        n2 = 0
                        for enemy2 in enemies:
                            enemyR = pygame.Rect(enemy2[1].x - 10, enemy2[1].y - 10, 40, 40)
                            if enemyR.colliderect(tileR):
                                if n != n2:
                                    collided = True
                            n2 += 1
                        if player.obj.rect.colliderect(tileR):
                            collided = True
                        if collided == False:
                            remove_tiles.append(tile_str)
            add_item('gel')
            alerts.append(['+gel', 0])
            enemies.pop(n)
            add_img_particles(enemy_img, (render_pos[0] + scroll_x, render_pos[1] + scroll_y))
            n -= 1
        if enemy_img != None:
            if tile_z != -1:
                ordered_render(enemy_img, render_pos)
        n += 1
    # Render Entities 1 -------------------------------------- #
    weapon_img = weapons[current_weapon]
    x = player.x
    y = player.y
    render_x = int(x / 32 * 14 - y / 32 * 14) + 9
    render_y = int(x / 32 * 7 + y / 32 * 7) - 12
    if player_standing == False:
        if random.randint(1, 5) == 1:
            dust.append([e.entity(render_x + 4, render_y + 18, 2, 2), random.randint(0, 20) / 20 - 0.5,
                         random.randint(0, 20) / 20 - 0.5, 0])
    # Handle Mouse ------------------------------------------- #
    MX, MY = pygame.mouse.get_pos()
    if lock_mouse == True:
        if MX < 10:
            pygame.mouse.set_pos(10, MY)
        if MX > WINDOWWIDTH - 10:
            pygame.mouse.set_pos(WINDOWWIDTH - 10, MY)
        if MY < 10:
            pygame.mouse.set_pos(MX, 10)
        if MY > WINDOWHEIGHT - 10:
            pygame.mouse.set_pos(MX, WINDOWHEIGHT - 10)
    MX /= WINDOWWIDTH
    MY /= WINDOWHEIGHT
    dis_x = MX - (render_x + 4 - scroll_x) / 300
    dis_y = MY - (render_y + 5 - scroll_y) / 200
    if abs(dis_x) + abs(dis_y) < 0.075:
        rate_x = 0
        rate_y = 0
    else:
        rate_x = dis_x / (abs(dis_x) + abs(dis_y))
        rate_y = dis_y / (abs(dis_x) + abs(dis_y))
    # Render Entities 2 -------------------------------------- #
    # dash gfx
    if dash_timer != -1:
        y = dash_start[1] - render_y
        x = dash_start[0] - render_x
        if (x == 0) and (y == 0):
            x = 1
            y = 1
        slope = [x / (abs(x) + abs(y)), y / (abs(x) + abs(y))]
        perp_slope = [-slope[1], slope[0]]
        perp_slope2 = [slope[1], -slope[0]]
        d = 10 - dash_timer
        points = [[dash_start[0] - scroll_x, dash_start[1] - scroll_y],
                  [render_x + 4 - scroll_x + perp_slope[0] * d, render_y + 18 - scroll_y + perp_slope[1] * d],
                  [render_x + 4 - scroll_x - int(x / 2), render_y + 18 - scroll_y - int(y / 2)],
                  [render_x + 4 - scroll_x + perp_slope2[0] * d, render_y + 18 - scroll_y + perp_slope2[1] * d]]
        pygame.draw.polygon(display, (169, 59, 59), points)
    # actual entities
    weapon_rot = rot.point_degrees(((render_x - scroll_x) / 300, (render_y - scroll_y) / 200), (MX, MY))
    if attack_timer != -1:
        weapon_rot = attack_timer
        if weapon_rot > 720:
            weapon_rot = 720
        weapon_rot += attack_base
        weapon_gfx_img = pygame.transform.rotate(e.get_frame(gen_id(current_weapon, int(attack_timer / 45))).copy(),
                                                 attack_base)
    weapon_img = pygame.transform.rotate(weapon_img, -weapon_rot)
    if weapon_rot < 0:
        weapon_rot += 360
    if attack_timer != -1:
        display.blit(weapon_gfx_img, (render_x - scroll_x - int(weapon_gfx_img.get_width() / 2) + 3,
                                      render_y - scroll_y - int(weapon_gfx_img.get_height() / 2) + 9))
    z = -1
    if weapon_rot % 360 < 180:
        z = 1
    ordered_render(weapon_img, (render_x - scroll_x - int(weapon_img.get_width() / 2) + 3,
                                render_y - scroll_y - int(weapon_img.get_height() / 2) + 9),
                   render_y - scroll_y + player_img.get_height(), z)
    ordered_render(player_img, (render_x - scroll_x, render_y - scroll_y))
    scroll_x += (render_x - 150 - scroll_x) / 20
    scroll_y += (render_y - 100 - scroll_y) / 20

    for_render.sort()
    for img in for_render:
        display.blit(image_cache[img[4]], (img[2], img[3]))
    for_render = []
    image_cache = []
    # Dust --------------------------------------------------- #
    n = 0
    for particle in dust:
        particle[0].x += particle[1]
        particle[0].y += particle[2]
        if particle[0].animation == None:
            particle[0].animation = dust_anim
        ordered_render(particle[0].get_current_img().copy(), (particle[0].x - scroll_x, particle[0].y - scroll_y))
        particle[0].change_frame(1)
        particle[3] += 1
        if particle[3] >= 31:
            dust.pop(n)
            n -= 1
        n += 1
    # Projectiles -------------------------------------------- #
    for projectile in projectiles:
        obj = e.PhysicsObject(projectile[0], projectile[1], 20, 20)
        collisions = obj.move([projectile[2] * 3, projectile[3] * 3], get_nearby_tiles((obj.x, obj.y), tiles))
        for c in collisions:
            if collisions[c] == True:
                projectile[2] *= -1
                projectile[3] *= -1
        projectile[0] = obj.x
        projectile[1] = obj.y
        projectile[4] += 1
        render_pos = (int(projectile[0] / 32 * 14 - projectile[1] / 32 * 14) - scroll_x,
                      int(projectile[0] / 32 * 7 + projectile[1] / 32 * 7) - scroll_y)
        display.blit(shot_img, render_pos)
        if obj.rect.colliderect(player.obj.rect):
            projectile[2] *= -1
            projectile[3] *= -1
            e_dis_x = obj.x - player.x
            e_dis_y = obj.y - player.y
            if (e_dis_x == 0) and (e_dis_y == 0):
                e_dis_x = 1
                e_dis_y = 1
            e_rate_x = e_dis_x / (abs(e_dis_x) + abs(e_dis_y))
            e_rate_y = e_dis_y / (abs(e_dis_x) + abs(e_dis_y))
            player_knockback[0] -= e_rate_x * 4
            player_knockback[1] -= e_rate_y * 4
            health -= 2
            hurt += 10
    # Alerts ------------------------------------------------- #
    n = 0
    for alert in alerts:
        alert_w = get_text_width(alert[0], 1)
        alert_surf = pygame.Surface((alert_w, 8))
        text.show_text(alert[0], 0, 0, 1, 99999, font_1, alert_surf)
        alert_surf.set_colorkey((0, 0, 0))
        alert_surf.set_alpha(510 - alert[1] * 51)
        display.blit(alert_surf, (render_x - scroll_x + 4 - int(alert_w / 2), render_y - scroll_y - 10 - int(alert[1])))
        alert[1] += 0.2
        if alert[1] > 10:
            alerts.pop(n)
            n -= 1
        n += 1
    # GUI ---------------------------------------------------- #
    display.blit(bars_img, (0, 0))
    if health > 0:
        health_bar = pygame.Surface((int(health) + 1, 3))
        health_bar.fill((169, 59, 59))
        pygame.draw.line(health_bar, (16, 30, 41), (int(health), 0), (int(health), 3))
        display.blit(health_bar, (5, 5))
    if energy > 0:
        energy_bar = pygame.Surface((int(energy) + 1, 3))
        energy_bar.fill((63, 199, 120))
        pygame.draw.line(energy_bar, (16, 30, 41), (int(energy), 0), (int(energy), 3))
        display.blit(energy_bar, (5, 12))
    energy += 0.45
    if current_weapon == 'sword_1':
        energy += 0.15
    elif current_weapon == 'sword_2':
        energy += 0.3
    elif current_weapon == 'sword_3':
        energy += 0.35
    if energy > 50:
        energy = 50
    minutes = int(time_alive / (40 * 60))
    seconds = int((time_alive - minutes * (40 * 60)) / 40)
    milliseconds = int((time_alive - minutes * (40 * 60) - seconds * 40) * 2.5)
    time_str = str(minutes) + ':' + str(seconds) + ':' + str(milliseconds)
    text.show_text(time_str, 300 - get_text_width(time_str, 1) - 1, 1, 1, 99999, font_0, display)
    y = 30
    for slot in inventory:
        if slot[0] == None:
            slot[2] += (-30 - slot[2]) / 5
        else:
            slot[2] += (1 - slot[2]) / 5
            if 1 - slot[2] < 1:
                slot[2] = 1
        display.blit(slot_img, (int(slot[2]), y))
        if slot[0] != None:
            display.blit(item_images[slot[0]], (int(slot[2]) + 4, y + 4))
        if slot[0] == 'apples':
            if health < 80:
                health += 20
                slot[1] -= 1
                if slot[1] <= 0:
                    slot[0] = None
                    slot[1] = 0
                alerts.append(['-apples +health', 0])
        if slot[0] == 'gel':
            if current_weapon == 'sword_0':
                if slot[1] >= 60:
                    current_weapon = 'sword_1'
                    slot[1] -= 60
                    alerts.append(['-60 gel +sword', 0])
                    if slot[1] == 0:
                        slot[0] = None
            if current_weapon == 'sword_1':
                if slot[1] >= 150:
                    current_weapon = 'sword_2'
                    slot[1] -= 150
                    alerts.append(['-150 gel +sword', 0])
                    if slot[1] == 0:
                        slot[0] = None
            if current_weapon == 'sword_2':
                if slot[1] >= 300:
                    current_weapon = 'sword_3'
                    slot[1] -= 300
                    alerts.append(['-300 gel +sword', 0])
                    if slot[1] == 0:
                        slot[0] = None
        text.show_text(str(slot[1]), int(slot[2]) + 19 - get_text_width(str(slot[1]), 1), y + 13, 1, 99999, font_1,
                       display)
        y += 25
    display.blit(weapon_slot, (1, 177))
    display.blit(weapon_items[current_weapon], (5, 182))
    if new_game > 0:
        controls_img.set_alpha(new_game * 4)
        display.blit(controls_img, (112, 30))
    # Buttons ------------------------------------------------ #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_UP:
                directions[0] = True
            if event.key == K_RIGHT:
                directions[1] = True
            if event.key == K_DOWN:
                directions[2] = True
            if event.key == K_LEFT:
                directions[3] = True
            if event.key == K_m:
                if lock_mouse == False:
                    lock_mouse = True
                else:
                    lock_mouse = False
            if event.key == K_p:
                paused = True
            if event.key == K_F11:
                if WINDOWWIDTH == 600:
                    WINDOWWIDTH = 900
                    WINDOWHEIGHT = 600
                else:
                    WINDOWWIDTH = 600
                    WINDOWHEIGHT = 400
                screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
        if event.type == KEYUP:
            if event.key == K_UP:
                directions[0] = False
            if event.key == K_RIGHT:
                directions[1] = False
            if event.key == K_DOWN:
                directions[2] = False
            if event.key == K_LEFT:
                directions[3] = False
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if attack_timer == -1:
                    if energy > 15:
                        energy -= 15
                        attack_timer = 0
                        attack_base = weapon_rot
                        attack_s.play()
                    else:
                        for item in inventory:
                            if item[0] == 'blueberries':
                                item[1] -= 1
                                if item[1] == 0:
                                    item[0] = None
                                energy += 50
                                alerts.append(['-blueberries +energy', 0])
                        if energy > 15:
                            energy -= 15
                            attack_timer = 0
                            attack_base = weapon_rot
                            attack_s.play()
                        else:
                            alerts.append(['No Energy!', 0])
            if event.button == 3:
                if dash_timer == -1:
                    if energy > 10:
                        energy -= 10
                        dash_timer = 0
                        dash_start = [render_x + 4, render_y + 18]
                        dash_s.play()
                    else:
                        for item in inventory:
                            if item[0] == 'blueberries':
                                item[1] -= 1
                                if item[1] == 0:
                                    item[0] = None
                                energy += 50
                                alerts.append(['-blueberries +energy', 0])
                        if energy > 10:
                            energy -= 10
                            dash_timer = 0
                            dash_start = [render_x + 4, render_y + 18]
                            dash_s.play()
                        else:
                            alerts.append(['No Energy!', 0])
    # Update ------------------------------------------------- #
    time_alive += 1
    if hurt > 0:
        hurt -= 1
        hurt_surf = pygame.Surface((300, 200))
        hurt_surf.fill((169, 59, 59))
        hurt_surf.set_alpha(cap(hurt * 4, 180))
        if hurt > 60:
            hurt = 60
        display.blit(hurt_surf, (0, 0))
    frame_ms = get_ms() - last_frame
    last_frame = get_ms()
    FPS = int(1000 / frame_ms)
    # text.show_text('FPS: ' + str(FPS),1,21,1,99999,font_0,display)
    while paused:
        screen_shake = 0
        text.show_text('Paused', 150 - int(get_text_width('Paused', 1) / 2), 96, 1, 99999, font_1, display)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_p:
                    paused = False
                if event.key == K_F11:
                    if WINDOWWIDTH == 600:
                        WINDOWWIDTH = 900
                        WINDOWHEIGHT = 600
                    else:
                        WINDOWWIDTH = 600
                        WINDOWHEIGHT = 400
                    screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
        screen.blit(pygame.transform.scale(display, (WINDOWWIDTH, WINDOWHEIGHT)), (
        random.randint(0, cap(int(screen_shake), 5) * 2) - int(screen_shake),
        random.randint(0, cap(int(screen_shake), 5) * 2) - int(screen_shake)))
        pygame.display.update()
        mainClock.tick(40)
    while health <= 0:
        screen_shake = 0
        text.show_text('You died in ' + time_str + '.',
                       150 - int(get_text_width('You died in ' + time_str + '.', 1) / 2), 90, 1, 99999, font_1, display)
        text.show_text('Press R to restart.', 150 - int(get_text_width('Press R to restart.', 1) / 2), 100, 1, 99999,
                       font_1, display)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_F11:
                    if WINDOWWIDTH == 600:
                        WINDOWWIDTH = 900
                        WINDOWHEIGHT = 600
                    else:
                        WINDOWWIDTH = 600
                        WINDOWHEIGHT = 400
                    screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
                if event.key == K_r:
                    health = 100
                    energy = 50
                    attack_timer = -1
                    dash_timer = -1
                    enemies = []
                    tiles = {'0;0': ['grass', 0, 0, 0], '0;1': ['grass', 0, 1, 0], '1;0': ['grass', 1, 0, 0],
                             '1;1': ['grass', 1, 1, 0]}
                    scroll_x = -100
                    scroll_y = -50
                    player = e.entity(0, 0, 20, 20)
                    new_game = 180
                    current_weapon = 'sword_0'
                    player_knockback = [0, 0]
                    hurt = 0
                    new_tile_timer = 0
                    particles = []
                    time_alive = 1
                    explosions = []
                    inventory = [[None, 0, -30], [None, 0, -30], [None, 0, -30], [None, 0, -30]]
                    decor = {}
                    dust = []
                    projectiles = []
                    remove_tiles = []
                    next_enemy = None
        screen.blit(pygame.transform.scale(display, (WINDOWWIDTH, WINDOWHEIGHT)), (
        random.randint(0, cap(int(screen_shake), 5) * 2) - int(screen_shake),
        random.randint(0, cap(int(screen_shake), 5) * 2) - int(screen_shake)))
        pygame.display.update()
        mainClock.tick(40)
    screen.blit(pygame.transform.scale(display, (WINDOWWIDTH, WINDOWHEIGHT)), (
    random.randint(0, cap(int(screen_shake), 5) * 2) - int(screen_shake),
    random.randint(0, cap(int(screen_shake), 5) * 2) - int(screen_shake)))
    if screen_shake > 0:
        screen_shake -= 0.5
    if screen_shake > 10:
        screen_shake = 10
    pygame.display.update()
    mainClock.tick(40)
