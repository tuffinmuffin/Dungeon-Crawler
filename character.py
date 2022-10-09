from argparse import Action
from typing import Tuple
import pygame
import math

import constants

from enum import Enum

class Character():

    class Action(Enum):
        IDLE = 0
        RUN = 1


    def __init__(self, x: int, y: int, health: float, mob_anim_list: dict[str,list[pygame.Surface]], mob_key: str):
        self._flip = False
        self._animation_list = mob_anim_list
        self._mob_key = mob_key
        self.rect = pygame.Rect(0, 0, 40, 40)
        self.rect.center = (x,y)
        self._frame_index = 0
        self._update_time = pygame.time.get_ticks()

        self._action = self.Action.IDLE.value
        self._is_char_running = False #start in idle

        self.health = health



    def draw(self, screen: pygame.Surface):
        flipped_image = pygame.transform.flip(
            self._animation_list[self._mob_key][self._action][self._frame_index], self._flip, False)
        if self._mob_key == constants.ELF_KEY:
            screen.blit(flipped_image, (self.rect.x, self.rect.y - constants.OFFSET * constants.SCALE))
        else:
            screen.blit(flipped_image, self.rect)
        pygame.draw.rect(screen, constants.RED, self.rect, 1)

    def is_alive(self) -> bool:
        return self.health > 0

    def update(self):
        #check if alive
        if self.health <= 0:
            self.health = 0

        animation_cooldown = 70

        #check what action player is performing
        if self._is_char_running:
            self.update_action(self.Action.RUN)
        else:
            self.update_action(self.Action.IDLE)

        #handle animation
        #update image index
        if pygame.time.get_ticks() - self._update_time > animation_cooldown:
            self._frame_index = (self._frame_index + 1) % len(self._animation_list[self._mob_key][self._action])
            self._update_time = pygame.time.get_ticks()

    def move(self, dx: int, dy: int):
        #control diagonal speed
        if dx != 0 and dy != 0:
            dx = dx * (math.sqrt(2)/2)
            dy = dy * (math.sqrt(2)/2)

        self.rect.x += dx
        self.rect.y += dy
        if dx != 0:
            self._flip = True if dx <0 else False
        self._is_char_running = True if dx != 0 or dy != 0 else False

    def update_action(self, new_action: Action):
        act_val = new_action.value
        if(self._action != act_val):
            self._action = act_val
            #update animation settings
            self._frame_index = 0
            self._update_time = pygame.time.get_ticks()


    def get_center(self) -> Tuple[int, int]:
        return self.rect.center

