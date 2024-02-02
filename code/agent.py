import pygame
from entity import *
from settings import *
from support import *

class Agent(Entity):
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer):
        super().__init__(pos, group, collision_sprites, tree_sprites, interaction, soil_layer, "agent")

    def update(self, dt):
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        
        self.move(dt)
        self.animate(dt)
    