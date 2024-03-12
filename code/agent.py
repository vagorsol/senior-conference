import pygame
import math
from player import Player
from entity import *
from settings import *
from support import *
from sprites import Generic
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement

class Agent(Entity):
    def __init__(self, pos, player, group, collision_sprites, tree_sprites, interaction, soil_layer, tree_layer, grid, screen, all_sprites):
        super().__init__(pos, group, collision_sprites, tree_sprites, interaction, soil_layer, "agent")
        
        self.player = player
        self.direction.x = 0
        self.tree_layer = tree_layer
        self.grid = grid
        self.finder = AStarFinder(diagonal_movement = DiagonalMovement.never) 
        self.screen = screen
        self.all_sprites = all_sprites
        self.RESET_POS = pygame.math.Vector2(pos[0], pos[1])

    def draw_path(self, path):
        for point in path:
            x = point.x * TILE_SIZE
            y = point.y * TILE_SIZE

            point_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            point_surf.fill('BLACK')
            point_rect = point_surf.get_rect()
            point_rect.x = x
            point_rect.y = y
            Generic((x, y), point_surf, self.all_sprites)   
    
    def check_target_intersect(self, target):
        ceil_pos = (math.ceil(self.pos.x / TILE_SIZE),
                    math.ceil(self.pos.y / TILE_SIZE))
        floor_pos = (int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))
        
        if(ceil_pos != target 
           and floor_pos != target 
           and (ceil_pos[0], floor_pos[1]) != target 
           and (floor_pos[0], ceil_pos[1]) != target
        ):
            return False
        else:
            return True

    def move(self, target, dt):        
        start = self.grid.node(int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))
        end = self.grid.node(int(target.x), int(target.y)) 
        path, path_status = self.finder.find_path(start, end, self.grid)
        self.grid.cleanup()

        if (path_status and path):
            path.pop(0)
            
            if(path and not self.check_target_intersect((end.x, end.y))):
                self.direction = (pygame.math.Vector2((path[0].x + 0.5)  * TILE_SIZE, (path[0].y + 0.5) * TILE_SIZE) 
                                  - pygame.math.Vector2(self.pos.x, self.pos.y)).normalize()
            else:
                self.direction = pygame.math.Vector2(0, 0)
                # flag for when arrived
                # enum - success / fail
                # this code should go into a different function since the move is the actually moving it function
        else: 
            self.direction = pygame.math.Vector2(0, 0)
        
        # setting the walking animation
        if self.direction.y > 0:
            self.status = 'down'
        elif self.direction.y < 0:
            self.status = 'up' 
        if self.direction.x > 0 and self.direction.x > self.direction.y:
            self.status = 'right'
        elif self.direction.x < 0 and self.direction.x < self.direction.y:
            self.status = 'left' 
        super().move(dt) 

    def update(self, dt):
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        
        # 15, 7
        target = pygame.math.Vector2(37, 23)
        # stops at ~ 36, 23
        self.move(target, dt)
        self.animate(dt)
        # for behavior make list and cycle through
    
    def reset(self):
        self.pos = pygame.math.Vector2(self.RESET_POS.x, self.RESET_POS.y)