import pygame
from typing import List, Dict

from character import Character
from items import Item, ItemType


import constants
from constants import TileData, TileList

class World():

    def __init__(self) -> None:
        self.reset_state()

    def reset_state(self):
        self.map_tiles = []
        self.obstacle_tiles = []
        self.items = []
        self.exit_tiles = []
        self.player = None
        self.monsters = []
        self.level = None

    def getTileData(self, tile_list, tile, x, y) -> TileData:
        image = tile_list[tile]
        image_rect = image.get_rect()
        image_x = x * constants.TILE_SIZE
        image_y = y * constants.TILE_SIZE
        image_rect.center = (image_x, image_y)
        return [image, image_rect, image_x, image_y]

    def process_data(self, level: int, data: List[List[int]], tile_list : List[pygame.Surface], item_dict, animation_dict, weapon_small_dict = None, clear = True):
        #reset states
        self.reset_state()
        self.level = level
        if clear:
            self.map_tiles = []
        default_floor_tile = 0
        self.level_length = len(data)

        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                tile_data = self.getTileData(tile_list, tile, x, y)

                match tile:
                    case 7: #wall
                        self.obstacle_tiles.append(tile_data)
                    case 8: # exit
                        self.exit_tiles.append(tile_data)
                    case 9: #coin
                        item = Item(tile_data[2], tile_data[3], ItemType.COIN, item_dict)
                        self.items.append(item)
                        tile_data = self.getTileData(tile_list, default_floor_tile, x, y)
                    case 10: #hp potion
                        item = Item(tile_data[2], tile_data[3], ItemType.HP_POT, item_dict)
                        self.items.append(item)
                        tile_data = self.getTileData(tile_list, default_floor_tile, x, y)
                    case 11: #player
                        self.player = Character(tile_data[2], tile_data[3], 100, animation_dict, constants.ELF_KEY, True)
                        tile_data = self.getTileData(tile_list, default_floor_tile, x, y)
                    case 12: #imp
                        self.monsters.append(Character(tile_data[2], tile_data[3], 100, animation_dict, constants.IMP_KEY))
                        tile_data = self.getTileData(tile_list, default_floor_tile, x, y)
                    case 13: #Skeleton
                        self.monsters.append(Character(tile_data[2], tile_data[3], 100, animation_dict, constants.SKELTON_KEY))
                        tile_data = self.getTileData(tile_list, default_floor_tile, x, y)
                    case 14: #goblin
                        self.monsters.append(Character(tile_data[2], tile_data[3], 100, animation_dict, constants.GOBLIN_KEY))
                        tile_data = self.getTileData(tile_list, default_floor_tile, x, y)
                    case 15: #muddy
                        self.monsters.append(Character(tile_data[2], tile_data[3], 100, animation_dict, constants.MUDDY_KEY))
                        tile_data = self.getTileData(tile_list, default_floor_tile, x, y)
                    case 16: #tine zombie
                        self.monsters.append(Character(tile_data[2], tile_data[3], 100, animation_dict, constants.ZOMBIE_KEY))
                        tile_data = self.getTileData(tile_list, default_floor_tile, x, y)
                    case 17: #Big Demon
                        self.monsters.append(Character(tile_data[2], tile_data[3], 100, animation_dict,
                                                       constants.BIG_DEMON_KEY, is_boss=True, size=2, small_weapon_list=weapon_small_dict))
                        tile_data = self.getTileData(tile_list, default_floor_tile, x, y)

                #add image data to main tile lists
                if tile >= 0:
                    self.map_tiles.append(tile_data)

    def get_exits(self) -> TileList:
        return self.exit_tiles

    def get_items(self) -> List[Item]:
        return self.items

    def get_player(self) -> Character:
        return self.player

    def get_monster(self) -> List[Character]:
        return self.monsters

    def get_obstacles(self) -> TileList:
        return self.obstacle_tiles

    def update(self, screen_scroll: List[int]):
        for tile in self.map_tiles:
            tile[2] += screen_scroll[0]
            tile[3] += screen_scroll[1]
            tile[1].center = (tile[2], tile[3])

    def draw(self, surface: pygame.Surface):
        for tile in self.map_tiles:
            surface.blit(tile[0], tile[1])

    def get_level(self) -> int:
        return self.level