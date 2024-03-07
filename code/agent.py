import player
import py_trees
import sys
from entity import *
from settings import *
from support import *
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement

class Agent(Entity):
    def __init__(self, pos, player, group, collision_sprites, tree_sprites, interaction, soil_layer, tree_layer, grid):
        super().__init__(pos, group, collision_sprites, tree_sprites, interaction, soil_layer, "agent")
        
        self.player = player
        self.direction.x = 0
        self.tree_layer = tree_layer
        self.grid = grid
        self.finder = AStarFinder(diagonal_movement = DiagonalMovement.always) 

    def move(self, target, dt):
        start = self.grid.node(int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))
        end = self.grid.node(int(target.x), int(target.y)) 
        path, path_status = self.finder.find_path(start, end, self.grid)
        self.grid.cleanup()

        # because int, cannot do in between grids
        # most likely wil need to revisit this later
        # potential pathing issues: because the grid-based-ness, can get caught
        # in between objects not accounted for in the grid. also can possibly not reach some areas
        # so have to run a "can i get there" check first
        # TODO: grid pathing funkiness check
        if (path_status):
            path.pop(0)
            if(path):
                self.direction = (
                    pygame.math.Vector2(path[0].x, path[0].y) - pygame.math.Vector2(start.x, start.y)).normalize()
            else:
                self.direction = pygame.math.Vector2(0, 0)
        else: 
            self.direction = pygame.math.Vector2(0, 0)
        
        # setting the walking animation
        if self.direction.y >= 1:
            self.status = 'down'
        elif self.direction.y <= -1:
            self.status = 'up'
        if self.direction.x >= 1:
            self.status = 'right'
        elif self.direction.x <= -1:
            self.status = 'left'
        super().move(dt) 

    def nearest_coor(self, lst):
        # TODO: point in a list from current position that has the shortest path
        # given a list of points, return the point that a) can be reached from tphe current location and 
        # b) has the shortest path. then return the point i guess??
        # (probably should return the path too so i don't have to recalculate it... time efficiency woo!!)
        start = self.grid.node(int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))
        return_point = start
        min_len = sys.maxsize # set to some large number. tbd
        for coor in lst: 
            # print(coor)
            end = self.grid.node(int(coor.x), int(coor.y)) 
            path, path_status = self.finder.find_path(start, end, self.grid)
            self.grid.cleanup()
            if (path_status and len(path) < min_len):
                return_point = coor
        return return_point

    def choose_target(self):
        point = self.nearest_coor(self.tree_layer)
        return point

    def update(self, dt):
        self.get_status()
        self.update_timers()
        self.get_target_pos()
       
        #15, 7
        target = pygame.math.Vector2(16, 12)
        # self.move(target, dt)
        self.animate(dt)
    