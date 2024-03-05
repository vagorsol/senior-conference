import player
import py_trees
import math
from entity import *
from settings import *
from support import *
from pathfinding.core.grid import Grid


class Agent(Entity):
    def __init__(self, pos, player, group, collision_sprites, tree_sprites, interaction, soil_layer, grid):
        super().__init__(pos, group, collision_sprites, tree_sprites, interaction, soil_layer, "agent")
        
        self.player = player
        self.direction.x = 1

    def move(self, target, dt):
        # get player size
        # make target position behind player
        
        # get agent to do an "errand" (click on map and it goes there?)
        print(self.pos.x // TILE_SIZE, self.pos.y // TILE_SIZE)
        self.direction.x = (self.player.pos.x - self.pos.x)
        self.direction.y = (self.player.pos.y - self.pos.y)
        b = self.direction.length() - 50
        self.direction = self.direction.normalize() * b
        self.direction.x = math.floor(self.direction.x)
        self.direction.y = math.floor(self.direction.y)
        # print(self.direction)

        # setting the walking animation (need to tune this)
        if self.direction.y >= 1:
            self.status = 'down'
        elif self.direction.y <= -1:
            self.status = 'up'
        if self.direction.x >= 1:
            self.status = 'right'
        elif self.direction.x <= -1:
            self.status = 'left'
        super().move(dt) 

    def update(self, dt):
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        # print(self.pos.x // TILE_SIZE, self.pos.y // TILE_SIZE)
        self.move(dt)
        self.animate(dt)
    