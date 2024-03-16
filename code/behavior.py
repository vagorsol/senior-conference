import sys
from status import Status
from timer import Timer
from settings import *
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement 

class Behavior():
    def __init__(self, agent, list, grid):
        self.agent = agent
        self.list = list
        self.grid = grid
        self.finder = AStarFinder(diagonal_movement = DiagonalMovement.never)

        # setting as none because need to make the other behavior BEFORE linking them
        self.status = Status.NOT_RUNNING
        self.next_behavior = None 
        # TODO: status and ticks()

    def set_path(self, pos, lst):
        start = self.grid.node(int(pos.x // TILE_SIZE), int(pos.y // TILE_SIZE))
        min_len = sys.maxsize
        path_status = False
        nearest_coor = start

        for coor in lst: 
            end = self.grid.node(int(coor.x), int(coor.y)) 
            path, path_status = self.finder.find_path(start, end, self.grid)
            self.grid.cleanup()
            if (path_status and len(path) < min_len):
                nearest_coor = end 
        self.agent.target = nearest_coor  
    
    def set_next_behavior(self, behavior):
        self.next_behavior = behavior

    def action(self):
        pass
    # TODO: have the actions be loopable (don't progress to the next one until a "failure" happens)

    def update(self):
        # if the agent is not moving, set a target
        if (self.agent.movement == Status.NOT_RUNNING and self.status == Status.NOT_RUNNING):
            self.set_path(self.agent.pos, self.list)
        else:
            if (self.agent.movement == Status.SUCCESS):
                self.agent.movement = Status.NOT_RUNNING
                self.status = Status.RUNNING
                self.action()
            elif (self.agent.movement == Status.FAILURE):
                # reset statuses
                self.agent.movement = Status.NOT_RUNNING
                self.status = Status.NOT_RUNNING

                # set current behavior to this's next behavior
                self.agent.curr_behavior = self.next_behavior
        # also TODO gotta have this action loop until can't do anything, i.e. list is empty. wahoo

class WaterBehavior(Behavior):
    def __init__(self, agent, list, grid):
        super().__init__(agent, list, grid) 
        
    def action(self):
        # set the agent's selected tool to watering can and use it
        self.agent.tool_index = 2 
        self.agent.timers['tool use'].activate()

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
        
    def action(self):
        # set the agent's selected tool to axe and then swing
        # TODO: for tree, need some way of knowing that it is done (i.e., tree is "dead")
        self.agent.selected_tool = 1 
        self.agent.timers['tool use'].activate()