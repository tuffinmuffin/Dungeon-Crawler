from ast import Constant
import constants
from character import Character
from weapon import Weapon, Arrow

import pygame
import glob
import os
import pathlib


from collections.abc import Iterable

pygame.init()


screen = pygame.display.set_mode(constants.SCREEN_SIZE)
pygame.display.set_caption("Dungeon Crawler")

#create clock for update loop
clock = pygame.time.Clock()

#define player movement variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False

font = pygame.font.Font(constants.FONT_PATH, 20)

#help to scale image
def  scale_img(image : pygame.Surface, scale: float):
    w = image.get_width() * scale
    h = image.get_height() * scale
    return pygame.transform.scale(image, (w,h))

def load_animation(path: str):
    animation_list = []
    for f in glob.iglob(path + "\*" ):
        animation_list.append(scale_img(pygame.image.load(f).convert_alpha(), constants.SCALE))
    return animation_list

def load_animations(path: str):
    animation_dict = {}
    for mob_folder in glob.iglob(path + "\*"):
        animation_list = []
        mob_name = os.path.basename(mob_folder)
        for anim_action_f in glob.iglob(mob_folder + "\*"):
            animation_list.append(load_animation(anim_action_f))
        animation_dict[mob_name] = animation_list

    return animation_dict

def load_images(path: str, scale = None):
    images = {}
    for f in glob.iglob(path + "\*"):
        name = pathlib.Path(os.path.basename(f)).stem
        image = pygame.image.load(f).convert_alpha()
        if scale:
            image = scale_img(image, scale)
        images[name] = image
    return images


class DamageText(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, damage: float, color):
        super().__init__()
        self.image = font.render(str(damage), True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        #float damage text
        self.rect.y -= 1

        #delete after a few seconds
        self.counter += 1
        if self.counter > 30:
            self.kill()




#load assets
animation_dict = load_animations(constants.ANIM_PATH)
weapon_dict = load_images(constants.WEAPON_PATH, constants.WEAPON_SCALE)
item_dict = load_images(constants.ITEMS_PATH)

#create player
player = Character(100, 100, 100, animation_dict, constants.ELF_KEY)
bow = Weapon(weapon_dict["bow"], weapon_dict["arrow"])

#create enemy
enemy = Character(200, 300, 100, animation_dict, constants.IMP_KEY)

# create enemy list

enemy_list: list[Character] = []
enemy_list.append(enemy)


#create sprite groups
arrow_group = pygame.sprite.Group()

damage_text_group = pygame.sprite.Group()

#main game loop
run = True
while run:

    #control max frame rate
    clock.tick(constants.FPS)

    screen.fill(constants.BG)

    #calculate player movement
    player_dx = 0
    player_dy = 0

    player_dx = moving_right - moving_left # right +
    player_dy = moving_down - moving_up # down +

    player.move(player_dx, player_dy)

    #update player
    player.update()
    arrow = bow.update(player)

    for arror in arrow_group:
        damage, damage_pos = arror.update(enemy_list)

        if damage:
            x = damage_pos.centerx
            y = damage_pos.y
            damage_text_group.add(DamageText(x, y, damage, constants.RED))

    damage_text_group.update()
    if arrow:
        arrow_group.add(arrow)

    for enemy in enemy_list:
        enemy.update()


    #draw player
    player.draw(screen)
    bow.draw(screen)
    arrow_group.draw(screen)
    damage_text_group.draw(screen)

    #draw enemy
    for enemy in enemy_list:
        enemy.draw(screen)

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
