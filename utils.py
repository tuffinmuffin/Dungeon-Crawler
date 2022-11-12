import pygame
import glob
import os
import pathlib
import csv
from typing import List, Dict
from collections.abc import Iterable
from character import Character
from items import ItemType

import constants

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

#function to output text to screen
def draw_text(screen: pygame.Surface, text: str, font : pygame.font.Font, text_col : pygame.color , x : int, y : int):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#function to display game info
def draw_info(screen: pygame.Surface, player: Character, level: int, item_dict, font: pygame.font.Font):
    #draw panel
    pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 50))
    pygame.draw.line(screen, constants.WHITE, (0, 50), (constants.SCREEN_WIDTH, 50))

    #draw lives
    for i in range(5):
        #health per heart = 20
        heart = None
        resid_health = player.get_health() - i * constants.HEALTH_PER_HEART
        heart_dict = item_dict[ItemType.HEART.name]
        if resid_health <= 0:
            heart = heart_dict[constants.EMPTY_HEART_KEY]
        elif resid_health < constants.HEALTH_PER_HEART:
            heart = heart_dict[constants.HALF_HEART_KEY]
        else:
            heart = heart_dict[constants.FULL_HEART_KEY]

        screen.blit(heart, (10+ i * 50, 0))

    #Level
    draw_text(screen, "LEVEL: " + str(level), font, constants.WHITE, constants.SCREEN_WIDTH / 2, 15)

    #show score
    draw_text(screen, f"X{player.get_score()}", font, constants.WHITE, constants.SCREEN_WIDTH - 100, 15)

class DamageText(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, damage: float, color, font: pygame.font.Font):
        super().__init__()
        self.image = font.render(str(damage), True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self, screen_scroll: List[int]):
        #reposition based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        #float damage text
        self.rect.y -= 1

        #delete after a few seconds
        self.counter += 1
        if self.counter > 30:
            self.kill()

#load in level data
def load_level(level : int, path : str = f"levels"):
    #level_data = [[-1]* constants.LEVEL_ROWS] * constants.LEVEL_COLS
    level_data = []
    file = f"{path}{os.path.sep}level{level}_data.csv"
    try:
        with open(file , newline="") as csvFile:
            reader = csv.reader(csvFile, delimiter=",")
            for row in reader:
                row_data = []
                for tile in row:
                    row_data.append(int(tile))
                level_data.append(row_data)
    except FileNotFoundError as err:
        print(f"Failed to load level {level} at {file}")
        exit(1)

    return level_data