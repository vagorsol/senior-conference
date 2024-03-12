import sys
from timer import Timer
from settings import *
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement 

class Behavior():
    def _init_(self, agent, list, grid):
        self.agent = agent
        self.list = list
        self.grid = grid
        self.finder = AStarFinder(diagonal_movement = DiagonalMovement.never)

        # setting as none because need to make the other 
        # behavior BEFORE linking them
        self.next_behavior = None 
        # TODO: status and ticks()
    
    def nearest_path(self, pos, lst):
        start = self.grid.node(int(pos.x // TILE_SIZE), int(pos.y // TILE_SIZE))
        min_len = sys.maxsize
        path_status = False
        nearest_coor = start
        shortest_path = []
        for coor in lst: 
            end = self.grid.node(int(coor.x), int(coor.y)) 
            path, path_status = self.finder.find_path(start, end, self.grid)
            self.grid.cleanup()
            if (path_status and len(path) < min_len):
                nearest_coor = end
                shortest_path = path    
        return nearest_coor, shortest_path, path_status
    
    def select_path(self):
        coor,_ ,_ = self.nearest_path(self.agent.pos, self.list) 
        return coor
    
    def set_next_behavior(self, behavior):
        self.next_behavior = behavior

class WaterBehavior(Behavior):
    def _init_(self, agent, list, grid):
        super()._init_(agent, list, grid) 
        
   # todo: rename these
    def action(self):
        # set the agent's selected tool to watering can 
        self.agent.tool_index = 2 
        self.agent.timers['tool use'].activate()

class SeedBehavior(Behavior):
    def _init_(self, agent, list, grid):
        super()._init_(agent, list, grid)   

class HarvestBehavior(Behavior):
    def _init_(self, agent, list, grid):
        super()._init_(agent, list, grid)   
        # need "list of fully grown plant" tiles
        # or maybe it's just "if picked something up, place it in bin"

class TreeBehavior(Behavior):
    def _init_(self, agent, tree_layer, grid):
        super()._init_(agent, tree_layer, grid)  
        
    def action(self):
        # set the agent's selected tool to axe
        self.agent.selected_tool = 1 
        self.agent.timers['tool use'].activate()