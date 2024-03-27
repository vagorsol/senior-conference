import pygame, sys
from support import Status, Direction
from timer import Timer
from settings import *
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement 

DIRECTIONS = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]

class Behavior():
    def __init__(self, agent, list, grid):
        self.agent = agent
        self.list = list
        self.grid = grid
        self.finder = AStarFinder(diagonal_movement = DiagonalMovement.never)

        # setting as none because need to make the other behavior BEFORE linking them
        self.status = Status.NOT_RUNNING
        self.next_behavior = None 

    def set_path(self, pos):
        start = self.grid.node(int(pos.x // TILE_SIZE), int(pos.y // TILE_SIZE))
        min_len = sys.maxsize
        nearest_coor = None

        for coor in self.list:      
            end = self.grid.node(int(coor.x), int(coor.y))         
            path = self.finder.find_path(start, end, self.grid)
            self.grid.cleanup()
            
            if (path and len(path[0]) < min_len):
                min_len = len(path[0])
                nearest_coor = end 
        self.agent.target = nearest_coor 
    
    def set_next_behavior(self, behavior):
        self.next_behavior = behavior

    def action(self):
        pass

    def update(self):
        if (self.list):
            # print(self.agent.movement, self.status)
            # a - isn't always in the hit box (this is movement debugging, it picks the right one, though
            # ^ this is "how do i get it to point in the direction of the tile"
            # ARGHHHHH LOGIC!!!! MATH!! COMPLICATED MATHS AND LOGIC!!!
            # b - when multiple unwatered tiles, stays on the singular tile
            #  and c - FUNKY
            # water only list of tiles at beginning
            # flag to tile?
            if (self.agent.movement == Status.NOT_RUNNING and self.status == Status.NOT_RUNNING):
                self.set_path(self.agent.pos)
            else:
                if (self.agent.movement == Status.SUCCESS):
                    self.agent.movement = Status.NOT_RUNNING
                    self.status = Status.RUNNING     
                   
                elif (self.agent.movement == Status.FAILURE):
                    self.agent.movement = Status.NOT_RUNNING
                    self.status = Status.FAILURE
                if (self.status == Status.RUNNING): 
                    if (not self.agent.timers['tool use'].active):
                        self.action() 
                    else: 
                        self.status = Status.NOT_RUNNING
                        self.agent.movement = Status.NOT_RUNNING
        else:
            self.status = Status.NOT_RUNNING
            self.agent.movement = Status.NOT_RUNNING
    
    def reset(self):
        self.status = Status.NOT_RUNNING
        
class WaterBehavior(Behavior):
    def __init__(self, agent, list, grid):
        super().__init__(agent, list, grid) 
        
    def action(self):
        # set the agent's selected tool to watering can and use it
        self.agent.tool_index = 2
        self.agent.selected_tool = self.agent.tools[self.agent.tool_index]
        self.agent.timers['tool use'].activate()

class TreeBehavior(Behavior):
    def __init__(self, agent, list, grid):
        super().__init__(agent, list, grid)  
        
    def set_path(self, pos, lst):
        start = self.grid.node(int(pos.x // TILE_SIZE), int(pos.y // TILE_SIZE))
        min_len = sys.maxsize
        nearest_coor = None

        for coor in lst: 
            for dir in DIRECTIONS:   
                end = self.grid.node(int(coor.x)  + dir.value[0], int(coor.y) + dir.value[1]) 
                path,_ = self.finder.find_path(start, end, self.grid)
                self.grid.cleanup()
                if (path and len(path) < min_len):
                    nearest_coor = end 
        self.agent.target = nearest_coor  
       
    def action(self):
        # set the agent's selected tool to axe and then swing
        self.agent.tool_index = 1
        self.agent.selected_tool = self.agent.tools[self.agent.tool_index]
        self.agent.timers['tool use'].activate()

class IdleBehavior(Behavior):
    def __init__(self, agent, grid, reset_pos):
        list = [pygame.math.Vector2(reset_pos[0] // TILE_SIZE, reset_pos[1] // TILE_SIZE)]
        super().__init__(agent, list, grid)
        self.next_behavior = self