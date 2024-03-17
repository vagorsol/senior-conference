import pygame, math
from player import Player
from behavior import WaterBehavior, SeedBehavior, TreeBehavior, IdleBehavior
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
        self.RESET_POS = pygame.math.Vector2(pos[0], pos[1])
        self.movement = Status.NOT_RUNNING
        self.target = None

        # pathfinding debugging values
        self.screen = screen
        self.all_sprites = all_sprites

        # set up the behavior tree
        self.setup()

    def setup(self):
        # print(self.soil_layer.unwatered_tiles)
        water_behavior = WaterBehavior(self, self.soil_layer.unwatered_tiles, self.grid)
        seed_behavior = SeedBehavior(self, self.soil_layer.empty_soil_tiles, self.grid)
        tree_behavior = TreeBehavior(self, self.tree_layer, self.grid)
        idle_behavior = IdleBehavior(self, self.grid, self.RESET_POS)

        # behavior chain
        water_behavior.set_next_behavior(water_behavior)
        # water_behavior.set_next_behavior(seed_behavior)
        # seed_behavior.set_next_behavior(tree_behavior)
        # tree_behavior.set_next_behavior(idle_behavior)

        # should test action first i think
        self.curr_behavior =  water_behavior # tree_behavior

    # pathing debugging function
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
    
        if(ceil_pos == target 
           or floor_pos == target 
           or (ceil_pos[0], floor_pos[1]) == target 
           or (floor_pos[0], ceil_pos[1]) == target
        ):
            return True
        else:
            return False

    def move(self, dt):        
        start = self.grid.node(int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))
        end = self.grid.node(int(self.target.x), int(self.target.y)) 
        path,_ = self.finder.find_path(start, end, self.grid)
        self.grid.cleanup()
        # print(path)
        if (path):
            path.pop(0)
            # print(self.check_target_intersect((end.x, end.y)))
            if(path and not self.check_target_intersect((end.x, end.y))):
                self.direction = (pygame.math.Vector2((path[0].x + 0.5)  * TILE_SIZE, (path[0].y + 0.5) * TILE_SIZE) 
                                  - pygame.math.Vector2(self.pos.x, self.pos.y)).normalize()
                self.movement = Status.RUNNING # flag for "currently moving"
            else:
                self.direction = pygame.math.Vector2(0, 0)
                self.movement = Status.SUCCESS # flag for arrival
        else: 
            self.direction = pygame.math.Vector2(0, 0)
            self.movement = Status.FAILURE # flag for failure
        
        # setting the walking animation
        if self.direction.y > 0:
            self.status = 'down'
        elif self.direction.y < 0:
            self.status = 'up' 
        if self.direction.x > 0 and self.direction.x > self.direction.y:
            self.status = 'right'
        elif self.direction.x < 0 and self.direction.x < self.direction.y:
            self.status = 'left' 
        # self.draw_path(path)
        super().move(dt) 

    def update(self, dt):
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        
        # print(self.soil_layer.unwatered_tiles)
        # target = pygame.math.Vector2(37, 23)
        if (self.curr_behavior and self.curr_behavior.status != Status.FAILURE):
            self.curr_behavior.update()
        else:
            # set current behavior to this's next behavior
            self.curr_behavior.status = Status.NOT_RUNNING
            self.curr_behavior = self.curr_behavior.next_behavior
        if (self.movement is not Status.SUCCESS and self.target):
            self.move(dt)
        self.animate(dt)
    
    def reset(self):
        self.pos = pygame.math.Vector2(self.RESET_POS.x, self.RESET_POS.y)