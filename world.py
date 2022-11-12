import pygame
from typing import List, Dict

from items import Item, ItemType

import constants



class World():

    def __init__(self) -> None:
        self.map_tiles = []
        self.obstacle_tiles = []
        self.items = []
        self.exit_tile = None

    def process_data(self, data: List[List[int]], tile_list : List[pygame.Surface], item_dict, clear = True):
        if clear:
            self.map_tiles = []
        self.level_length = len(data)

        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                image = tile_list[tile]
                image_rect = image.get_rect()
                image_x = x * constants.TILE_SIZE
                image_y = y * constants.TILE_SIZE
                image_rect.center = (image_x, image_y)
                tile_data = [image, image_rect, image_x, image_y]

                if tile == 7:
                    self.obstacle_tiles.append(tile_data)
                elif tile == 8:
                    self.exit_tile = tile_data
                elif tile == 9: #coin
                    coin = Item(image_x, image_y, ItemType.COIN, item_dict)
                    self.items.append(coin)
                elif tile == 10: #hp potion
                    potion = Item(image_x, image_y, ItemType.HP_POT, item_dict)
                    self.items.append(coin)



                #add image data to main tile lists
                if tile >= 0:
                    self.map_tiles.append(tile_data)

    def get_items(self):
        return self.items

    def update(self, screen_scroll: List[int]):
        for tile in self.map_tiles:
            tile[2] += screen_scroll[0]
            tile[3] += screen_scroll[1]
            tile[1].center = (tile[2], tile[3])


    def draw(self, surface: pygame.Surface):
        for tile in self.map_tiles:
            surface.blit(tile[0], tile[1])
