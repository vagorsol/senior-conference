import pygame 
from pathfinding.core.grid import Grid
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu
from agent import Agent

class Level:
	def __init__(self):

		# get the display surface
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.nav_collision = pygame.sprite.Group()
		self.tree_sprites = pygame.sprite.Group()
		self.interaction_sprites = pygame.sprite.Group()

		self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
		self.setup()
		self.overlay = Overlay(self.player)
		self.transition = Transition(self.reset, self.player)

		# sky
		self.rain = Rain(self.all_sprites)
		self.raining = randint(0,10) > 7
		self.soil_layer.raining = self.raining
		self.sky = Sky()

		# shop
		self.menu = Menu(self.player, self.toggle_shop)
		self.shop_active = False

		# music
		# self.success = pygame.mixer.Sound('../audio/success.wav')
		# self.success.set_volume(0.3)
		# self.music = pygame.mixer.Sound('../audio/music.mp3')
		# self.music.play(loops = -1)

	def setup(self):
		tmx_data = load_pygame('../data/map.tmx')
		
		# house 
		for layer in ['HouseFloor', 'HouseFurnitureBottom']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

		for layer in ['HouseWalls', 'HouseFurnitureTop']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites)

		# Fence
		for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
			Generic((x * TILE_SIZE,y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites, self.nav_collision])

		# water 
		water_frames = import_folder('../graphics/water')
		for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
			Water((x * TILE_SIZE,y * TILE_SIZE), water_frames, self.all_sprites)

		# trees 
		for obj in tmx_data.get_layer_by_name('Trees'):
			Tree(
				pos = (obj.x, obj.y), 
				surf = obj.image, 
				groups = [self.all_sprites, self.collision_sprites, self.tree_sprites, self.nav_collision], 
				name = obj.name,
				player_add = self.player_add)

		# wildflowers 
		for obj in tmx_data.get_layer_by_name('Decoration'):
			WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites, self.nav_collision])

		# collion tiles
		for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites, self.nav_collision)

		self.create_pathing_grid()
		
		# Player 
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':
				self.player = Player(
					pos = (obj.x,obj.y), 
					group = self.all_sprites, 
					collision_sprites = self.collision_sprites,
					tree_sprites = self.tree_sprites,
					interaction = self.interaction_sprites,
					soil_layer = self.soil_layer,
					toggle_shop = self.toggle_shop)
			
			if obj.name == 'Bed':
				Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

			if obj.name == 'Trader':
				Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)
			if obj.name == 'Agent_Start':
				self.agent = Agent(
					pos = (obj.x,obj.y), 
					player = self.player,
					group = self.all_sprites, 
					collision_sprites = self.collision_sprites,
					tree_sprites = self.tree_sprites,
					interaction = self.interaction_sprites,
					soil_layer = self.soil_layer,
					grid = self.grid
				)


		Generic(
			pos = (0,0),
			surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
			groups = self.all_sprites,
			z = LAYERS['ground'])

	def player_add(self,item):

		self.player.item_inventory[item] += 1
		self.success.play()

	def toggle_shop(self):

		self.shop_active = not self.shop_active

	def reset(self):
		# plants
		self.soil_layer.update_plants()

		# soil
		self.soil_layer.remove_water()
		self.raining = randint(0,10) > 7
		self.soil_layer.raining = self.raining
		if self.raining:
			self.soil_layer.water_all()

		# apples on the trees
		for tree in self.tree_sprites.sprites():
			for apple in tree.apple_sprites.sprites():
				apple.kill()
			tree.create_fruit()

		# sky
		self.sky.start_color = [255,255,255]

	def plant_collision(self):
		if self.soil_layer.plant_sprites:
			for plant in self.soil_layer.plant_sprites.sprites():
				if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
					self.player_add(plant.plant_type)
					plant.kill()
					Particle(plant.rect.topleft, plant.image, self.all_sprites, z = LAYERS['main'])
					self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

	def run(self,dt):
		
		# drawing logic
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.player)
		
		# updates
		if self.shop_active:
			self.menu.update()
		else:
			self.all_sprites.update(dt)
			self.plant_collision()

		# weather
		self.overlay.display()
		if self.raining and not self.shop_active:
			self.rain.update()
		self.sky.display(dt)

		# transition overlay
		if self.player.sleep:
			self.transition.play()
	
	def create_pathing_grid(self):
		ground = pygame.image.load('../graphics/world/ground.png')
		h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE

		# how to get all collidble sprites but also not the player or self. uh. hm. 
		# for sprite in self.collision_sprites.sprites():
		# 	if hasattr(sprite, 'hitbox'):
		# 		sprite_rect = sprite.image.get_rect()
		# 		print(pygame.math.Vector2(sprite_rect.center))
				
		self.matrix = [[1 for col in range(h_tiles)] for row in range(v_tiles)]
		for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Collision').tiles():
			self.matrix[y][x] = 0
		# house edge cases
		for i in range(20, 27):
			self.matrix[i][19] = 0
			self.matrix[i][20] = 0
			self.matrix[i][27] = 0
			self.matrix[i][28] = 0
		for sprite in self.nav_collision.sprites():
			if hasattr(sprite, 'hitbox'):
				self.matrix[sprite.rect.top // TILE_SIZE][sprite.rect.left // TILE_SIZE] = 0
				
		self.grid = Grid(range(h_tiles), range(v_tiles), self.matrix)


class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()

	def custom_draw(self, player):
		self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
		self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

		for layer in LAYERS.values():
			for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
				if sprite.z == layer:
					offset_rect = sprite.rect.copy()
					offset_rect.center -= self.offset
					self.display_surface.blit(sprite.image, offset_rect)

					# # anaytics
					# if sprite == player:
					# 	pygame.draw.rect(self.display_surface,'red',offset_rect,5)
					# 	hitbox_rect = player.hitbox.copy()
					# 	hitbox_rect.center = offset_rect.center
					# 	pygame.draw.rect(self.display_surface,'green',hitbox_rect,5)
					# 	target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
					# 	pygame.draw.circle(self.display_surface,'blue',target_pos,5)