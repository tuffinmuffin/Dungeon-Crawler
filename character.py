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


    def __init__(self, x: int, y: int, health: float, mob_anim_list: dict[str,list[pygame.Surface]], mob_key: str, is_player = False):
        self._flip = False
        self._score = 0
        self._animation_list = mob_anim_list
        self._mob_key = mob_key
        self.rect = pygame.Rect(0, 0, constants.TILE_SIZE, constants.TILE_SIZE)
        self.rect.center = (x,y)
        self._frame_index = 0
        self._update_time = pygame.time.get_ticks()

        self._action = self.Action.IDLE.value
        self._is_char_running = False #start in idle

        self._health = health
        self._is_player = is_player



    def draw(self, screen: pygame.Surface):
        flipped_image = pygame.transform.flip(
            self._animation_list[self._mob_key][self._action][self._frame_index], self._flip, False)
        if self._mob_key == constants.ELF_KEY:
            screen.blit(flipped_image, (self.rect.x, self.rect.y - constants.OFFSET * constants.SCALE))
        else:
            screen.blit(flipped_image, self.rect)
        pygame.draw.rect(screen, constants.RED, self.rect, 1)

    def is_alive(self) -> bool:
        return self._health > 0

    def ai(self, screen_scroll):
        #reposition based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]


    def update(self):
        #check if alive
        if self._health <= 0:
            self._health = 0

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
        screen_scroll = [0, 0]

        #control diagonal speed
        if dx != 0 and dy != 0:
            dx = dx * (math.sqrt(2)/2)
            dy = dy * (math.sqrt(2)/2)

        self.rect.x += dx
        self.rect.y += dy
        if dx != 0:
            self._flip = True if dx <0 else False
        self._is_char_running = True if dx != 0 or dy != 0 else False

        #only scroll if player
        if self._is_player:
            #update scroll based on player postion

            #move camera left/right
            if self.rect.right > (constants.SCREEN_WIDTH -  constants.SCROLL_THRESH):
                screen_scroll[0] = (constants.SCREEN_WIDTH -  constants.SCROLL_THRESH) - self.rect.right
                self.rect.right = constants.SCREEN_WIDTH -  constants.SCROLL_THRESH

            if self.rect.left < constants.SCROLL_THRESH:
                screen_scroll[0] = constants.SCROLL_THRESH - self.rect.left
                self.rect.left = constants.SCROLL_THRESH

            # move camera up and down
            if self.rect.bottom > (constants.SCREEN_HEIGHT -  constants.SCROLL_THRESH):
                screen_scroll[1] = (constants.SCREEN_HEIGHT -  constants.SCROLL_THRESH) - self.rect.bottom
                self.rect.bottom = constants.SCREEN_HEIGHT -  constants.SCROLL_THRESH

            if self.rect.top < constants.SCROLL_THRESH:
                screen_scroll[1] = constants.SCROLL_THRESH - self.rect.top
                self.rect.top = constants.SCROLL_THRESH

        return screen_scroll

    def update_action(self, new_action: Action):
        act_val = new_action.value
        if(self._action != act_val):
            self._action = act_val
            #update animation settings
            self._frame_index = 0
            self._update_time = pygame.time.get_ticks()


    def get_center(self) -> Tuple[int, int]:
        return self.rect.center

    def change_health(self, healthDelta: int):
        self._health += healthDelta
        if self._health > 100:
            self._health = 100
        elif self._health < 0:
            self._health = 0

    def change_score(self, score: int):
        self._score += score
    def get_score(self) -> int:
        return self._score
    def get_health(self) -> int:
        return self._health