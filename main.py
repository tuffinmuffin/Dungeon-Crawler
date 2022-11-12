from ast import Constant
import constants
from character import Character
from weapon import Weapon, Arrow
from items import Item, ItemType
from world import World
import pygame

from utils import DamageText, draw_info, load_animations, load_images, load_level

pygame.init()

screen = pygame.display.set_mode(constants.SCREEN_SIZE)
pygame.display.set_caption("Dungeon Crawler")

#create clock for update loop
clock = pygame.time.Clock()

#define game variables
level = 1
screen_scroll = [0, 0]

#define player movement variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False

font = pygame.font.Font(constants.FONT_PATH, 20)

#load assets
animation_dict = load_animations(constants.ANIM_PATH)
weapon_dict = load_images(constants.WEAPON_PATH, constants.WEAPON_SCALE)
item_dict = {}
item_dict[ItemType.HEART.name] = load_images(constants.HEART_PATH, constants.HEART_SCALE)
item_dict[ItemType.COIN.name] = load_images(constants.COIN_PATH, constants.COIN_SCALE)
item_dict[ItemType.HP_POT.name] = load_images(constants.POT_PATH, constants.POT_SCALE)

#load tiles and convert to flat list ordered by name.
tile_dict  = load_images(constants.TILE_PATH, constants.SCALE)
tile_list = [tile_dict[str(i)] for i in range(len(tile_dict))]

#create world
"""
world_data = [
    [7, 7, 7, 7, 7],
    [7, 0, 1, 2, 7],
    [7, 3, 4, 5, 7],
    [7, 6, 6, 6, 7],
    [7, 7, 7, 7, 7],
]"""

#create empty tile list



world_data = load_level(level)

world = World()

#load sample level
world.process_data(world_data, tile_list, item_dict)



#create player
player = Character(400, 300, 100, animation_dict, constants.ELF_KEY, True)
bow = Weapon(weapon_dict["bow"], weapon_dict["arrow"])

#create enemy
enemy = Character(300, 300, 100, animation_dict, constants.IMP_KEY)

# create enemy list
enemy_list: list[Character] = []
enemy_list.append(enemy)


#create sprite groups
arrow_group = pygame.sprite.Group()
damage_text_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
item_group.add(*world.get_items())
#score coin
score_coin = Item(constants.SCREEN_WIDTH - 115, 23, ItemType.COIN, item_dict)

#pot = Item(200, 200, ItemType.HP_POT, item_dict)
#coin = Item(400, 400, ItemType.COIN, item_dict)
#item_group.add(pot)
#item_group.add(coin)

#main game loop
run = True
while run:
    #control max frame rate
    clock.tick(constants.FPS)

    screen.fill(constants.BG)

    #draw world
    world.draw(screen)


    #calculate player movement
    player_dx = 0
    player_dy = 0

    player_dx = moving_right - moving_left # right +
    player_dy = moving_down - moving_up # down +

    screen_scroll =  player.move(player_dx, player_dy)

    #update all objects
    player.update()
    arrow = bow.update(player)

    world.update(screen_scroll)

    for arror in arrow_group:
        damage, damage_pos = arror.update(enemy_list, screen_scroll)

        if damage:
            x = damage_pos.centerx
            y = damage_pos.y
            damage_text_group.add(DamageText(x, y, damage, constants.RED, font))

    damage_text_group.update(screen_scroll)
    if arrow:
        arrow_group.add(arrow)

    for enemy in enemy_list:
        enemy.ai(screen_scroll)
        enemy.update()

    item_group.update(screen_scroll, player)

    #draw player
    player.draw(screen)
    bow.draw(screen)
    arrow_group.draw(screen)
    damage_text_group.draw(screen)
    item_group.draw(screen)

    #draw enemy
    for enemy in enemy_list:
        enemy.draw(screen)

    draw_info(screen, player, level ,item_dict, font)
    score_coin.update((0,0),None)
    score_coin.draw(screen)

    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            key_down = event.type == pygame.KEYDOWN
            match event.key:
                case pygame.K_a: # left
                    moving_left = constants.PLAYER_SPEED
                case pygame.K_d: # right
                    moving_right = constants.PLAYER_SPEED
                case pygame.K_w: # up
                    moving_up = constants.PLAYER_SPEED
                case pygame.K_s: # down
                    moving_down = constants.PLAYER_SPEED
        elif event.type == pygame.KEYUP:
            match event.key:
                case pygame.K_a: # left
                    moving_left = 0
                case pygame.K_d: # right
                    moving_right = 0
                case pygame.K_w: # up
                    moving_up = 0
                case pygame.K_s: # down
                    moving_down = 0

        if event.type == pygame.MOUSEBUTTONUP:
            bow.fired_reset()


    #draw to screen
    pygame.display.update()



pygame.quit()
