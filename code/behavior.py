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

    def set_path(self, pos, lst):
        start = self.grid.node(int(pos.x // TILE_SIZE), int(pos.y // TILE_SIZE))
        min_len = sys.maxsize
        nearest_coor = None

        for coor in lst: 
            end = self.grid.node(int(coor.x), int(coor.y)) 
            path = self.finder.find_path(start, end, self.grid)
            self.grid.cleanup()

            if (path and len(path) < min_len):
                nearest_coor = end 
        self.agent.target = nearest_coor  
    
    def set_next_behavior(self, behavior):
        self.next_behavior = behavior

    def action(self):
        pass

    def update(self):
        if (self.agent.movement == Status.NOT_RUNNING and self.status == Status.NOT_RUNNING):
            self.set_path(self.agent.pos, self.list)
        else:
            # TODO: do action just ONCE and not keep looping
            if (self.agent.movement == Status.SUCCESS):
                self.agent.movement = Status.NOT_RUNNING
                self.status = Status.RUNNING
                # print(not self.agent.timers['tool use'].active)
                # if (self.status == Status.RUNNING):
                #     self.status = Status.RUNNING
                #     self.status = Status.NOT_RUNNING
                #     self.action() 
                
            elif (self.agent.movement == Status.FAILURE):
                self.agent.movement = Status.NOT_RUNNING
                self.status = Status.NOT_RUNNING

            if (self.status == Status.RUNNING):
                self.status = Status.RUNNING
                self.status = Status.NOT_RUNNING
                if (not self.agent.timers['tool use'].active):
                    self.action() 
            # elif (self.agent.movement == Status.NOT_RUNNING and self.status == Status.RUNNING):
            #     # print(self.list)
            #     if (self.list):
            #         # print("print")
            #         print(self.timers['tool use'].active)
            #         if (not self.timers['tool use'].active):
            #             self.action()
            #         else:
            #             self.agent.use_tool()
            #     else:
            #         self.status == Status.Success

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
        # self.agent.tim 

class SeedBehavior(Behavior):
    def __init__(self, agent, list, grid):
        super().__init__(agent, list, grid)   
    
    def action(self):
        self.agent.timers['seed use'].activate()
        # need to pick seed and check that there are seeds to be planted first too

class HarvestBehavior(Behavior):
    def __init__(self, agent, list, grid):
        super().__init__(agent, list, grid)   
        # need "list of fully grown plant" tiles
        # or maybe it's just "if picked something up, place it in bin"

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
        # TODO: make sure is facing "right" direction after reaching destination
    def action(self):
        # set the agent's selected tool to axe and then swing
        self.agent.selected_tool = self.agent.tools[1]
        self.agent.timers['tool use'].activate()

    def update(self):
        if (self.agent.movement == Status.NOT_RUNNING and self.status == Status.NOT_RUNNING):
            self.set_path(self.agent.pos, self.list)
        else:
            if (self.agent.movement == Status.SUCCESS):
                self.status = Status.RUNNING
                self.action()
                self.status = Status.NOT_RUNNING
            elif (self.agent.movement == Status.FAILURE):
                # reset statuses
                self.agent.movement = Status.NOT_RUNNING
                self.status = Status.FAILURE

            elif (self.agent.movement == Status.NOT_RUNNING and self.status == Status.RUNNING):
                if (self.list):
                    self.action()
                else:
                    self.status == Status.Success

class IdleBehavior(Behavior):
    def __init__(self, agent, grid, reset_pos):
        list = [pygame.math.Vector2(reset_pos[0] // TILE_SIZE, reset_pos[1] // TILE_SIZE)]
        super().__init__(agent, list, grid)
        self.next_behavior = self