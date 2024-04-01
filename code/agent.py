import pygame, math
from player import Player
from behavior import *
from entity import *
from settings import *
from support import *
from sprites import Generic
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement

class Agent(Entity):
    def __init__(self, pos, player, group, collision_sprites, tree_sprites, interaction, soil_layer, grid, screen, all_sprites, agent_mode):
        super().__init__(pos, group, collision_sprites, tree_sprites, interaction, soil_layer, "agent")
        
        self.player = player
        self.direction.x = 0
        self.grid = grid
        self.finder = AStarFinder(diagonal_movement = DiagonalMovement.never) 
        self.RESET_POS = pygame.math.Vector2(pos[0], pos[1])
        self.movement = Status.NOT_RUNNING.value
        self.target = None
        self.target_object = None
        self.mode = agent_mode
        self.curr_behavior_index = 0

        # pathfinding debugging values
        self.screen = screen
        self.all_sprites = all_sprites
        
        # set up the behavior tree
        self.setup()

    def setup(self):
        self.water_behavior = WaterBehavior(agent = self, 
                                            soil_tiles = self.soil_layer, 
                                            grid = self.grid, 
                                            weight = 5)
        self.tree_behavior = TreeBehavior(agent = self, 
                                          trees = self.tree_sprites, 
                                          grid = self.grid, 
                                          weight = 0.5)
        self.idle_behavior = IdleBehavior(agent = self, 
                                          grid = self.grid, 
                                          reset_pos = self.RESET_POS)

        self.behaviors = [self.idle_behavior, self.water_behavior, self.tree_behavior]

        self.curr_behavior =  self.idle_behavior
        
    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            self.curr_behavior_index = 1
        if keys[pygame.K_2]:
            self.curr_behavior_index = 2

    def select_behavior(self):
        if (self.mode == Mode.UTILITY.value):
            weight_water = self.water_behavior.weight * len(self.water_behavior.get_tiles())
            weight_trees = self.tree_behavior.weight * len(self.tree_behavior.get_tiles())

            if (weight_water >= weight_trees):
                self.curr_behavior = self.water_behavior
            elif (weight_water < weight_trees):
                self.curr_behavior = self.tree_behavior
            elif (weight_water == 0 and weight_trees == 0):
                self.curr_behavior = self.idle_behavior
        elif (self.mode == Mode.KEY.value):
            self.curr_behavior = self.behaviors[self.curr_behavior_index]
            # self.curr_behavior.
        else:
           self.curr_behavior = self.idle_behavior 

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

    def move(self, dt):        
        start = self.grid.node(int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))
        end = self.grid.node(int(self.target.x), int(self.target.y)) 
        path,_ = self.finder.find_path(start, end, self.grid)
        self.grid.cleanup()

        if (self.target_object):
            path.append(self.target_object)
        if (start == self.target_object):
            self.movement = Status.SUCCESS.value
            return
        
        if (path):
            path.pop(0)
            if (path):
                self.direction = (pygame.math.Vector2((path[0].x + 0.5)  * TILE_SIZE, (path[0].y + 0.25) * TILE_SIZE) 
                                  - pygame.math.Vector2(self.pos.x, self.pos.y)).normalize()
                self.movement = Status.RUNNING.value # flag for "currently moving"
            else:
                self.direction = pygame.math.Vector2(0, 0)
                self.movement = Status.SUCCESS.value # flag for arrival
        else: 
            self.direction = pygame.math.Vector2(0, 0)
            self.movement = Status.FAILURE.value # flag for failure
        
        # setting the walking animation
        if self.direction.y > 0:
            self.status = 'down'
        elif self.direction.y < 0:
            self.status = 'up' 
        if self.direction.x > 0 and abs(self.direction.x) > abs(self.direction.y):
            self.status = 'right'
        elif self.direction.x < 0 and abs(self.direction.x) > abs(self.direction.y):
            self.status = 'left' 
        # self.draw_path(path)
        super().move(dt) 

    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        
        # check if the behavior has finished running (either success or failure)    
        if (self.curr_behavior.status != Status.RUNNING.value):
            # select a new behavior
            self.target_status = None
            self.target_object = None
            self.target= None
            
            self.curr_behavior.reset()
            self.select_behavior()

            self.movement = Status.NOT_RUNNING.value
            self.curr_behavior.status = Status.RUNNING.value
        # key press where it can switch behavior mid-action (in theory)
        elif(self.mode == Mode.KEY.value):
            self.select_behavior()
            self.curr_behavior.update()
        if (self.movement is not Status.SUCCESS.value and self.target):
            self.move(dt)
        
        self.animate(dt)
    
    def reset(self):
        self.pos = pygame.math.Vector2(self.RESET_POS.x, self.RESET_POS.y)
        self.movement = Status.NOT_RUNNING.value
        self.curr_behavior = self.behaviors[0]

        for behavior in self.behaviors:
            behavior.reset()