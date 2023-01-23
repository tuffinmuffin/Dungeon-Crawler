from argparse import Action
from typing import Tuple
import pygame
import math

import constants
from constants import TileList

from enum import Enum
import weapon

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world import World

#from world import TileData, TileList
class Character():

    class Action(Enum):
        IDLE = 0
        RUN = 1


    def __init__(self,
                 x: int,
                 y: int,
                 health: float,
                 mob_anim_list: dict[str,list[pygame.Surface]],
                 mob_key: str,
                 is_player : bool= False,
                 is_boss : bool= False,
                 size :float = 1,
                 small_weapon_list: dict[str, pygame.Surface] = None):
        self._flip = False
        self._is_boss = is_boss
        self._score = 0
        self._animation_list = mob_anim_list
        self._small_weapon_list = small_weapon_list
        self._mob_key = mob_key
        self.rect = pygame.Rect(0, 0, constants.TILE_SIZE * size, constants.TILE_SIZE * size)
        self.rect.center = (x,y)
        self._frame_index = 0
        self._update_time = pygame.time.get_ticks()

        self._action = self.Action.IDLE.value
        self._is_char_running = False #start in idle

        self._health = health
        self._is_player = is_player

        self._last_hit = None
        self._stunned_until = 0
        self._last_attack = 0
        self._level_complete = None

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

    def ai(self, player: "Character", world: "World", screen_scroll : tuple[int, int]):
        obstacles = world.get_obstacles()
        spawns = []
        ai_dx = 0
        ai_dy = 0
        #reposition based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        #create line of sight from enemy to player
        line_of_sight = (self.rect.center, player.rect.center)
        clipped_line = None
        for obstacle in obstacles:
            if obstacle[1].clipline(line_of_sight):
                clipped_line = obstacle[1].clipline(line_of_sight)

        #check distance to player
        dist = math.sqrt(((self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2))


        #check if char can see player
        if not clipped_line and dist > constants.ENEMY_RANGE:
            ai_dx, ai_dy = self.home_move(player)

            #boss enemys shoot fireballs
            if self._is_boss:
                fireball_cooldown = 700
                if dist < 500:
                    if pygame.time.get_ticks() - self._last_attack >= fireball_cooldown:
                        self._last_attack = pygame.time.get_ticks()
                        spawns.append(weapon.Fireball(self._small_weapon_list, self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery))

        if (pygame.time.get_ticks() > self._stunned_until):
            self.move(ai_dx, ai_dy, world)

            #attack player
            if dist < constants.ATTACK_RANGE:
                player.hit(10)

        return spawns

    def hit(self, damage: int, stun: bool = 0, force : bool = False):
        if not self._last_hit or force:
            self._last_hit = pygame.time.get_ticks()
            self._stunned_until = pygame.time.get_ticks() + stun
            self.change_health(-damage)
            if stun:
                self._is_char_running = False


    def home_move(self, player: "Player") -> tuple[int, int]:
        dx = 0
        dy = 0
        #Simple Homing AI
        if self.rect.centerx > player.rect.centerx:
            dx = -constants.ENEMY_SPEED
        elif self.rect.centerx < player.rect.centerx:
            dx = constants.ENEMY_SPEED
        if self.rect.centery > player.rect.centery:
            dy = -constants.ENEMY_SPEED
        elif self.rect.centery < player.rect.centery:
            dy = constants.ENEMY_SPEED

        return (dx, dy)

    def update(self):
        #check if alive
        if self._health <= 0:
            self._health = 0

        #reset player taking a hit
        if self._is_player:
            hit_cooldown = 1000
            if self._last_hit and (pygame.time.get_ticks() - self._last_hit) > hit_cooldown:
                self._last_hit = None


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

    def move(self, dx: int, dy: int, world : "World"):
        obstacles = world.get_obstacles()
        screen_scroll = [0, 0]

        #control diagonal speed
        if dx != 0 and dy != 0:
            dx = dx * (math.sqrt(2)/2)
            dy = dy * (math.sqrt(2)/2)

        #check for collision with in x direction
        self.rect.x += dx

        for obstacle in obstacles:
            if obstacle[1].colliderect(self.rect):
                #check which direction player moved to select side
                if dx > 0:
                    self.rect.right = obstacle[1].left
                else:
                    self.rect.left = obstacle[1].right

        # check for collision in y
        self.rect.y += dy
        for obstacle in obstacles:
            if obstacle[1].colliderect(self.rect):
                #check which direction player moved to select side
                if dy > 0:
                    self.rect.bottom = obstacle[1].top
                else:
                    self.rect.top = obstacle[1].bottom

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

        if self._is_player:
            for player_exit in world.get_exits():
                if self.rect.collidepoint(player_exit[1].center):
                    self._level_complete = player_exit
                    break

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

    def set_health(self, health: int):
        self._health = health

    def change_score(self, score: int):
        self._score += score
    def get_score(self) -> int:
        return self._score
    def get_health(self) -> int:
        return self._health

    def get_level_complete(self, reset = True) -> bool:
        should_exit = True if self._level_complete else False
        if reset:
            self._level_complete = None
        return should_exit