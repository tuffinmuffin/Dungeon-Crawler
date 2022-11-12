import constants
from enum import Enum
import pygame
import character
from typing import List

class ItemType(Enum):
    COIN = 0
    HP_POT = 1
    HEART = 2

class Item(pygame.sprite.Sprite):
    def __init__(self, x : int, y : int, item_type : ItemType, animnation_list : dict[str,dict[str, pygame.Surface]], pos_fixed = False):
        super().__init__()
        self.item_type = item_type
        self.animation_list = animnation_list
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        if item_type == ItemType.COIN:
            self.keys = constants.COIN_KEY
        elif item_type == ItemType.HP_POT:
            self.keys = constants.POTION_RED_KEY
        self.image = self.animation_list[self.item_type.name][self.keys[self.frame_index]]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos_fixed = pos_fixed

    def update(self, screen_scroll: List[int], player: character.Character):

        #reposition based on screen scroll
        if not self.pos_fixed:
            self.rect.x += screen_scroll[0]
            self.rect.y += screen_scroll[1]

        animation_cooldown = 150

        #check for collisions
        if player:
            if self.rect.colliderect(player.rect):
                if self.item_type == ItemType.COIN:
                    player.change_score(1)
                elif self.item_type == ItemType.HP_POT:
                    player.change_health(10)

                #drop item
                self.kill()


        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index = (self.frame_index + 1) % len(self.keys)
            self.update_time = pygame.time.get_ticks()
            self.image = self.animation_list[self.item_type.name][self.keys[self.frame_index]]


    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)