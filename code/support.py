from os import walk
from enum import Enum 
import pygame

def import_folder(path):
	surface_list = []

	for _, __, img_files in walk(path):
		for image in img_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_list.append(image_surf)

	return surface_list

def import_folder_dict(path):
	surface_dict = {}

	for _, __, img_files in walk(path):
		for image in img_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_dict[image.split('.')[0]] = image_surf

	return surface_dict

class Status(Enum):
    SUCCESS = 0
    FAILURE = 1
    RUNNING = 2
    NOT_RUNNING = 3

class Direction(Enum):
	NORTH = (0, -1)
	SOUTH = (0, 1)
	EAST = (1, 0)
	WEST = (-1, 0)