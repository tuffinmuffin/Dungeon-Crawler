import constants
import pygame
import math

import random
from typing import List
from constants import TileList

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world import World
class Weapon():
    def __init__(self, image: pygame.Surface, projectile: pygame.Surface):
        self._image = image
        self._projectile = projectile
        self._angle = 0
        self._rect = self._image.get_rect()
        self._fired = False
        self._last_shot = 0

    def update(self, player):
        shot_cooldown = (self._last_shot + 300) > pygame.time.get_ticks()

        arrow = None
        self._rect.center = player.get_center()

        pos = pygame.mouse.get_pos()
        x_dist = pos[0] - self._rect.centerx
        #py game y coors decrease down screen
        y_dist = -(pos[1] - self._rect.centery)
        self._angle = math.degrees(math.atan2(y_dist, x_dist))

        #get mouseclick
        if pygame.mouse.get_pressed()[0] and not self._fired and not shot_cooldown:
            arrow = Arrow(self._projectile, self._rect.centerx, self._rect.centery, self._angle)
            self._last_shot = pygame.time.get_ticks()
            self._fired = True

        return arrow

    def draw(self, screen: pygame.Surface):
        rot_image = pygame.transform.rotate(self._image, self._angle)

        #cal the center of the rect
        rect = (self._rect.centerx - int(rot_image.get_width()/2), self._rect.centery - int(rot_image.get_height()/2))
        screen.blit(rot_image, rect)

    def fired_reset(self):
        self._fired = False

class Arrow(pygame.sprite.Sprite):
    def __init__(self, image : pygame.Surface, x: float, y: float, angle: float):
        super().__init__()
        self.image_org = image
        self._angle = angle
        self.image = pygame.transform.rotate(self.image_org, self._angle - 90.0)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

        #calculate x and y vel
        self.dx = math.cos(math.radians(angle)) * constants.ARROW_SPEED
        self.dy = -math.sin(math.radians(angle)) * constants.ARROW_SPEED


    def update(self, enemy_list: list["Character"], screen_scroll : tuple[int, int], obstacles : TileList):

        #reposition based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        damage = 0
        damage_pos = None

        #update sprite image
        self.rect.y += self.dy
        self.rect.x += self.dx

        #check if arrow has gone off screen
        if (self.rect.right < 0 or self.rect.left > constants.SCREEN_WIDTH or
             self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT):
             self.kill()

        #check collision between arrow and enemies
        for enemy in enemy_list:
            if enemy.is_alive() and enemy.rect.colliderect(self.rect):
                damage = 10 + random.randint(-5, 5)
                stun_cooldown = 100
                damage_pos = enemy.rect
                enemy.hit(damage, stun_cooldown, True)
                self.kill()
                break

        for obstacle in obstacles:
            if obstacle[1].collidepoint(self.rect.center):
                self.kill()

        return damage, damage_pos


class Fireball(pygame.sprite.Sprite):
    def __init__(self, image : pygame.Surface, x: float, y: float, target_x: float, target_y: float):
        super().__init__()
        self.image_org = image["fireball"]
        self._angle = math.degrees(math.atan2(-(target_y - y), target_x - x))
        self.image = pygame.transform.rotate(self.image_org, self._angle - 90.0)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

        #calculate x and y vel
        self.dx = math.cos(math.radians(self._angle)) * constants.FIREBALL_SPEED
        self.dy = -math.sin(math.radians(self._angle)) * constants.FIREBALL_SPEED


    def update(self, enemy_list: list["Character"], screen_scroll : tuple[int, int], world : "World"):
        damage = None
        damage_pos = None
        #reposition based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]
        #update sprite image
        self.rect.y += self.dy
        self.rect.x += self.dx

        #check if arrow has gone off screen
        if (self.rect.right < 0 or self.rect.left > constants.SCREEN_WIDTH or
             self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT):
             self.kill()

        #check collision between arrow and enemies
        for enemy in enemy_list:
            if enemy.is_alive() and enemy.rect.colliderect(self.rect):
                damage = 10 + random.randint(-5, 5)
                damage_pos = enemy.rect
                enemy.hit(damage, 0, True)
                self.kill()
                break

        for obstacle in world.get_obstacles():
            if obstacle[1].collidepoint(self.rect.center):
                self.kill()

        return damage, damage_pos
