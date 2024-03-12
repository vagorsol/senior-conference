import pygame
from entity import *
from settings import *
from support import *
from timer import Timer

class Player(Entity):
	def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop):
		super().__init__(pos, group, collision_sprites, tree_sprites, interaction, soil_layer, 'character')
		
		# timers 
		# self.timers = {
		# 	'tool use': Timer(350,self.use_tool),
		# 	'tool switch': Timer(200),
		# 	'seed use': Timer(350,self.use_seed),
		# 	'seed switch': Timer(200),
		# }

		# # tools 
		# self.tools = ['hoe','axe','water']
		# self.tool_index = 0
		# self.selected_tool = self.tools[self.tool_index]

		# # seeds 
		# self.seeds = ['corn', 'tomato']
		# self.seed_index = 0
		# self.selected_seed = self.seeds[self.seed_index]
		
		# inventory
		# self.item_inventory = {
		# 	'wood':   20,
		# 	'apple':  20,
		# 	'corn':   20,
		# 	'tomato': 20
		# }
		# self.seed_inventory = {
		# 'corn': 5,
		# 'tomato': 5
		# }
		# self.money = 200

		# interaction
		self.sleep = False
		self.toggle_shop = toggle_shop

	def input(self):
		keys = pygame.key.get_pressed()

		if not self.timers['tool use'].active and not self.sleep:
			# directions 
			if keys[pygame.K_UP] or keys[pygame.K_w]:
				self.direction.y = -1
				self.status = 'up'
			elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
				self.direction.y = 1
				self.status = 'down'
			else:
				self.direction.y = 0

			if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				self.direction.x = 1
				self.status = 'right'
			elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
				self.direction.x = -1
				self.status = 'left'
			else:
				self.direction.x = 0

			# tool use
			if keys[pygame.K_x]:
				self.timers['tool use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0

			# change tool
			if keys[pygame.K_q] and not self.timers['tool switch'].active:
				self.timers['tool switch'].activate()
				self.tool_index += 1
				self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
				self.selected_tool = self.tools[self.tool_index]

			# seed use
			if keys[pygame.K_c]:
				self.timers['seed use'].activate()
				self.direction = pygame.math.Vector2()
				self.frame_index = 0

			# change seed 
			if keys[pygame.K_e] and not self.timers['seed switch'].active:
				self.timers['seed switch'].activate()
				self.seed_index += 1
				self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
				self.selected_seed = self.seeds[self.seed_index]

			if keys[pygame.K_RETURN]:
				collided_interaction_sprite = pygame.sprite.spritecollide(self,self.interaction,False)
				if collided_interaction_sprite:
					if collided_interaction_sprite[0].name == 'Trader':
						self.toggle_shop()
					else:
						self.status = 'left_idle'
						self.sleep = True

	def update(self, dt):
		self.input()
		self.get_status()
		self.update_timers()
		self.get_target_pos()

		self.move(dt)
		self.animate(dt)

