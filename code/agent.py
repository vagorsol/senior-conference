import player
import py_trees
from entity import *
from settings import *
from support import *
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement

class Agent(Entity):
    def __init__(self, pos, player, group, collision_sprites, tree_sprites, interaction, soil_layer, grid):
        super().__init__(pos, group, collision_sprites, tree_sprites, interaction, soil_layer, "agent")
        
        self.player = player
        self.direction.x = 0
        self.grid = grid
        self.finder = AStarFinder(diagonal_movement = DiagonalMovement.always) 

    def move(self, target, dt):
        start = self.grid.node(int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))
        end = self.grid.node(int(target.x), int(target.y)) 
        path,_ = self.finder.find_path(start, end, self.grid)
        self.grid.cleanup()

        # because int, cannot do in between grids
        # most likely wil need to revisit this later
        path.pop(0)
        if(path):
            self.direction = (
                pygame.math.Vector2(path[0].x, path[0].y) - pygame.math.Vector2(start.x, start.y)).normalize()
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

    def update(self, dt):
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        #15, 7
        target = pygame.math.Vector2(16, 12)
        self.move(target, dt)
        self.animate(dt)
    