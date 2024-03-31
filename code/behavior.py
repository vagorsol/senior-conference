import pygame, sys
from support import Status, Direction
from settings import *
from sprites import Tree
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement 

DIRECTIONS = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]

class Behavior():
    def __init__(self, agent, grid, weight):
        self.agent = agent
        self.list = []
        self.grid = grid
        self.weight = weight
        self.finder = AStarFinder(diagonal_movement = DiagonalMovement.never)
        self.status = Status.NOT_RUNNING # setting status as not running by default

    def set_path(self):
        start = self.grid.node(int(self.agent.pos.x // TILE_SIZE), int(self.agent.pos.y // TILE_SIZE))
        min_len = sys.maxsize
        nearest_coor = None

        # print(self.list)
        for coor in self.list:      
            end = self.grid.node(int(coor.x), int(coor.y))         
            path = self.finder.find_path(start, end, self.grid)
            self.grid.cleanup()

            if (path and len(path[0]) < min_len):
                min_len = len(path[0])
                nearest_coor = end 
        self.agent.target = nearest_coor 

    def action(self):
        pass

    def update(self):
        if (self.list):
            
            # a - isn't always in the hit box (this is movement debugging, it picks the right one, though
            # ^ this is "how do i get it to point in the direction of the tile"
            # ARGHHHHH LOGIC!!!! MATH!! COMPLICATED MATHS AND LOGIC!!!
            if (self.agent.movement == Status.NOT_RUNNING):
                self.set_path()
            else:
                if (self.agent.movement == Status.SUCCESS):
                    self.agent.movement = Status.NOT_RUNNING
                elif (self.agent.movement == Status.FAILURE):
                    self.agent.movement = Status.NOT_RUNNING
                    self.status = Status.FAILURE
                if (self.status == Status.RUNNING and self.agent.movement == Status.NOT_RUNNING): 
                    if (not self.agent.timers['tool use'].active):
                        self.action() 
                    else: 
                        self.status = Status.SUCCESS
        else:
            self.status = Status.FAILURE
            self.agent.movement = Status.NOT_RUNNING
    
    def reset(self):
        self.status = Status.NOT_RUNNING
        
class WaterBehavior(Behavior):
    def __init__(self, agent, soil_tiles, grid, weight):
        self.soil_tiles = soil_tiles
        super().__init__(agent, grid, weight) 

    def get_tiles(self):
        self.list = []
        for index_row, row in enumerate(self.soil_tiles.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell and not 'W' in cell:
                    self.list.append(pygame.math.Vector2(index_col, index_row))
        # print(self.list)
        return self.list

    def action(self):
        # set the agent's selected tool to watering can and use it
        self.agent.tool_index = 2
        self.agent.selected_tool = self.agent.tools[self.agent.tool_index]
        self.agent.timers['tool use'].activate()

    # def update(self):
    #     self.list = self.get_tiles()
    #     super().update()
class TreeBehavior(Behavior):
    def __init__(self, agent, trees, grid, weight):
        self.trees = trees
        self.selected_tree = None
        super().__init__(agent, grid, weight)  

    def get_tiles(self):
        self.list = []
        for tree in self.trees:
            if tree.alive:
                self.list.append(tree)
        return self.list

    # tree chopping pathing is not right because stops right before it
    # how to for tree go to that and one additional   
    def set_path(self):
        start = self.grid.node(int(self.agent.pos.x // TILE_SIZE), int(self.agent.pos.y // TILE_SIZE))
        min_len = sys.maxsize
        nearest_coor = None

        for tree in self.list:
            if (type(tree) is Tree and tree.alive):
                coor = pygame.math.Vector2(tree.pos[0] // TILE_SIZE, tree.pos[1] // TILE_SIZE)
                # if (tree.pos[0], tree.pos[1]) in TREE_POS:
                #     coor = TREE_POS.get((tree.pos[0], tree[1]))
                # else:
                #   continue
                
                for dir in DIRECTIONS:   
                    end = self.grid.node(int(coor.x)  + dir.value[0], int(coor.y) + dir.value[1]) 
                    path,_ = self.finder.find_path(start, end, self.grid)
                    self.grid.cleanup()
                    if (path and len(path) < min_len):
                        nearest_coor = end 
                        self.selected_tree = tree
                        self.agent.target_object = self.grid.node(int(tree.pos[0] // TILE_SIZE), int(tree.pos[1] // TILE_SIZE))
        self.agent.target = nearest_coor  
       
    def action(self):
        # set the agent's selected tool to axe and then swing
        self.agent.tool_index = 1
        self.agent.selected_tool = self.agent.tools[self.agent.tool_index]
        self.agent.timers['tool use'].activate()
    
    def update(self):
        # set direction agent should face at the end of its movement
        if (self.agent.movement == Status.SUCCESS):
            face_dir = (pygame.math.Vector2((self.agent.pos.x + 0.5)  * TILE_SIZE, (self.agent.pos.y + 0.5) * TILE_SIZE) 
                                  - pygame.math.Vector2(self.selected_tree.pos[0], self.selected_tree.pos[1])).normalize()
            if face_dir.y > 0:
                self.agent.status = 'down'
            elif face_dir.y < 0:
                self.agent.status = 'up' 
            if face_dir.x > 0 and abs(face_dir.x) > abs(face_dir.y):
                self.agent.status = 'right'
            elif face_dir.x < 0 and abs(face_dir.x) > abs(face_dir.y):
                self.agent.status = 'left' 

        if (self.selected_tree is None or (type(self.selected_tree) is Tree and self.selected_tree.alive)):
            super().update() # WHY DO IT BE MOVING
            # why is it still moving?
        if (self.selected_tree is not None and not self.selected_tree.alive):
            self.status = Status.SUCCESS

class IdleBehavior(Behavior):
    def __init__(self, agent, grid, reset_pos):     
        super().__init__(agent, grid, 0)
        self.list = [pygame.math.Vector2(reset_pos[0] // TILE_SIZE, reset_pos[1] // TILE_SIZE)]