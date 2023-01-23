from ast import Constant
import constants
from character import Character
from weapon import Weapon, Arrow
from items import Item, ItemType
from world import World
import pygame
from pygame import mixer
from button import Button

from utils import DamageText, draw_info, load_animations, load_images, load_level, ScreenFade

mixer.init()

pygame.init()

screen = pygame.display.set_mode(constants.SCREEN_SIZE)
pygame.display.set_caption("Dungeon Crawler")

#create clock for update loop
clock = pygame.time.Clock()

#define game variables
level = 1

start_game = False
pause_game = False

start_intro = False


font = pygame.font.Font(constants.FONT_PATH, 20)

#load assets
animation_dict = load_animations(constants.ANIM_PATH)
weapon_dict = load_images(constants.WEAPON_PATH, constants.WEAPON_SCALE)
weapon_small_dict = load_images(constants.WEAPON_PATH, constants.WEAPON_SMALL_SCALE)
item_dict = {}
item_dict[ItemType.HEART.name] = load_images(constants.HEART_PATH, constants.HEART_SCALE)
item_dict[ItemType.COIN.name] = load_images(constants.COIN_PATH, constants.COIN_SCALE)
item_dict[ItemType.HP_POT.name] = load_images(constants.POT_PATH, constants.POT_SCALE)

button_dict = load_images(constants.BUTTON_PATH, constants.BUTTON_SCALE)

#load sounds
pygame.mixer.music.load("assets/audio/music.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

shot_fx = pygame.mixer.Sound("assets/audio/arrow_shot.mp3")
shot_fx.set_volume(0.5)
hit_fx = pygame.mixer.Sound("assets/audio/arrow_hit.wav")
hit_fx.set_volume(0.5)
coin_fx = pygame.mixer.Sound("assets/audio/coin.wav")
coin_fx.set_volume(0.5)
heal_fx = pygame.mixer.Sound("assets/audio/heal.wav")
heal_fx.set_volume(0.5)

#create buttons
start_button = Button(constants.SCREEN_WIDTH // 2 - 145, constants.SCREEN_HEIGHT // 2 - 150 ,button_dict["button_start"])
exit_button = Button(constants.SCREEN_WIDTH // 2 - 110, constants.SCREEN_HEIGHT // 2 + 50 ,button_dict["button_exit"])
restart_button = Button(constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 50 ,button_dict["button_restart"])
resume_button = Button(constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 150 ,button_dict["button_resume"])

#load tiles and convert to flat list ordered by name.
tile_dict  = load_images(constants.TILE_PATH, constants.SCALE)
tile_list = [tile_dict[str(i)] for i in range(len(tile_dict))]

world_data = load_level(level)
world = World()
player : Character = None

def update_world(new_game = False):
    #load sample level
    world.process_data(level, world_data, tile_list, item_dict, animation_dict, weapon_small_dict)

    #create player
    global player
    global bow
    global enemy_list
    global arrow_group
    global damage_text_group
    global enemy_proj_group
    global item_group
    global score_coin
    global screen_scroll

    global moving_left
    global moving_right
    global moving_up
    global moving_down

    #define player movement variables
    moving_left = False
    moving_right = False
    moving_up = False
    moving_down = False

    screen_scroll = [0, 0]

    if new_game:
        player = None

    #get score and health and presist
    score = None
    health = None
    if player:
        score = player.get_score()
        health = player.get_health()

    player = world.get_player()

    if score:
        player.change_score(score)
    if health:
        player.set_health(health)

    bow = Weapon(weapon_dict["bow"], weapon_dict["arrow"])

    # create enemy list
    enemy_list = world.get_monster()

    #create sprite groups
    arrow_group = pygame.sprite.Group()
    damage_text_group = pygame.sprite.Group()
    enemy_proj_group = pygame.sprite.Group()

    #populate level items
    item_group = pygame.sprite.Group()
    item_group.add(*world.get_items())

    #score coin
    score_coin = Item(constants.SCREEN_WIDTH - 115, 23, ItemType.COIN, item_dict)


#create screen fade
intro_fade = ScreenFade(screen, 1, constants.BLACK, 4)
death_fade = ScreenFade(screen, 2, constants.PINK, 4)

#main game loop
run = True
while run:

    if world.get_level() != level:
        #new game
        if level == 0:
            level = 1
            player = None

        world_data = load_level(level)
        update_world()

    #control max frame rated
    clock.tick(constants.FPS)

    if start_game == False:
        screen.fill(constants.MENU_BG)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
            pause_game = False
            level = 0
        if exit_button.draw(screen):
            run = False
    elif pause_game == True:
        screen.fill(constants.MENU_BG)
        if resume_button.draw(screen):
            pause_game = False
        if exit_button.draw(screen):
            run = False
    else:

        screen.fill(constants.BG)
        #draw world
        world.draw(screen)

        if player.is_alive():

            #calculate player movement
            player_dx = 0
            player_dy = 0

            player_dx = moving_right - moving_left # right +
            player_dy = moving_down - moving_up # down +

            screen_scroll =  player.move(player_dx, player_dy, world)

            #update all objects
            player.update()
            arrow = bow.update(player)

            world.update(screen_scroll)

            for proj in enemy_proj_group:
                proj.update([player], screen_scroll, world)

            for arror in arrow_group:
                damage, damage_pos = arror.update(enemy_list, screen_scroll, world.get_obstacles())

                if damage:
                    x = damage_pos.centerx
                    y = damage_pos.y
                    damage_text_group.add(DamageText(x, y, damage, constants.RED, font))
                    hit_fx.play()

            damage_text_group.update(screen_scroll)
            if arrow:
                arrow_group.add(arrow)
                shot_fx.play()
            for enemy in enemy_list:
                spawns = enemy.ai(player, world, screen_scroll)
                enemy_proj_group.add(spawns)
                enemy.update()
                if(enemy.get_health() == 0):
                    enemy_list.remove(enemy)

            item_group.update(screen_scroll, player, coin_fx, heal_fx)

        #draw player
        player.draw(screen)
        bow.draw(screen)
        arrow_group.draw(screen)
        damage_text_group.draw(screen)
        item_group.draw(screen)
        enemy_proj_group.draw(screen)

        #draw enemy
        for enemy in enemy_list:
            enemy.draw(screen)

        draw_info(screen, player, level ,item_dict, font)
        score_coin.update((0,0),None)
        score_coin.draw(screen)

        #check for level complete
        if player.get_level_complete():
            level += 1
            start_intro = True

        #show intro
        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.reset()

        if not player.is_alive():
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.reset()
                    start_intro = True
                    level = 0


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
                case pygame.K_ESCAPE:
                    pause_game = True
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
