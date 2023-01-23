import pygame
from typing import TypeAlias
#types
TileData : TypeAlias = tuple[ pygame.Surface, pygame.Rect, int, int]
TileList : TypeAlias = list[TileData]

#game params
FPS = 60

#Player params
PLAYER_SPEED = 5
ARROW_SPEED = 10
FIREBALL_SPEED = 4
HEALTH_PER_HEART = 20

#Enemy Params
ENEMY_SPEED = 4
ENEMY_RANGE = 50
ATTACK_RANGE = 60

#Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
SCALE = 3
BUTTON_SCALE = 1.0
WEAPON_SCALE = 1.5
WEAPON_SMALL_SCALE = 1.0
HEART_SCALE = 3
POT_SCALE = 4
COIN_SCALE = 4
OFFSET = 12
SCROLL_THRESH = 200

TILE_SIZE = 16* SCALE

#max level size
LEVEL_ROWS = 150
LEVEL_COLS = 150

#sprites

ANIM_TYPE = ("idle", "run")
ANIM_PATH = "assets/images/characters/"
ELF_KEY = "elf"
BIG_DEMON_KEY = "big_demon"
GOBLIN_KEY = "goblin"
IMP_KEY = "imp"
MUDDY_KEY = "muddy"
SKELTON_KEY = "skeleton"
ZOMBIE_KEY = "tiny_zombie"
FONT_PATH = "assets/fonts/AtariClassic.ttf"

WEAPON_PATH = "assets/images/weapons/"
HEART_PATH = "assets/images/items/heart/"
COIN_PATH = "assets/images/items/coin/"
POT_PATH = "assets/images/items/pot/"
TILE_PATH = "assets/images/tiles/"
BUTTON_PATH = "assets/images/buttons/"

FULL_HEART_KEY = "heart_full"
HALF_HEART_KEY = "heart_half"
EMPTY_HEART_KEY = "heart_empty"

POTION_RED_KEY = ["potion_red"]
COIN_KEY = ["coin_f0", "coin_f1", "coin_f2", "coin_f3"]



#colors
RED = (255,0,0)
WHITE = (255,255,255)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)
BG = (40, 25, 25)
MENU_BG = (130, 0, 0)
PANEL = (50, 50, 50)