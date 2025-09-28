import pygame
from sys import exit
from random import randint
from copy import deepcopy
import json
import math

#pygame init
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Sundrop Caves')
clock = pygame.time.Clock()
MID_SCREENX = 368
MID_SCREENY = 168
TILE_SIZE = (32, 32)

#Extract tiles from tilemap
tilemap = pygame.image.load('DwarvenDelve/DwarvenDelve/Background/CaveTilemap.png').convert_alpha()
TILE_WIDTH = 16
TILE_HEIGHT = 16
tiles = []
map_width, map_height = tilemap.get_size()
for y in range(0, map_height, TILE_HEIGHT):
    for x in range(0, map_width, TILE_WIDTH):
        rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
        tile = tilemap.subsurface(rect)
        scaled_tile = pygame.transform.scale(tile, TILE_SIZE)  # Double the size
        tiles.append(scaled_tile)

wall = [tiles[0], tiles[1], tiles[2]]
topLeft, topMid, topRight = tiles[12], tiles[13], tiles[14]
midLeft, mid, midRight = tiles[24], tiles[25], tiles[26]
botLeft, botMid, botRight = tiles[36], tiles[37], tiles[38]

#game init
player = {}
game_map = []
fog = []
save_data = {}

MAP_WIDTH = 0
MAP_HEIGHT = 0

WAREHOUSE_SIZE = 20
TURNS_PER_DAY = 20
WIN_GP = 500

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
minerals_per_node_max = {'copper': 5, 'silver': 3, 'gold': 2}
pickaxe_price = [50, 150]

prices = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)

#methods
def load_map(filename, map_struct):
    map_file = open(filename, 'r')
    global MAP_WIDTH
    global MAP_HEIGHT
    global game_map

    map_struct.clear()
    
    # TODO: Add your map loading code here
    map_struct = []
    for line in map_file:
        string = line.rstrip('\n')
        row = []
        for grid in string:
            row.append(grid)
        map_struct.append(row)

    game_map = map_struct

    MAP_WIDTH = len(map_struct[0])
    MAP_HEIGHT = len(map_struct)

    map_file.close()

def initialize_game(game_map, player):
    # initialize map
    load_map("level1.txt", game_map)

    # TODO: initialize fog
    global fog
    fog.clear()

    row = []
    for i in range(MAP_WIDTH):
        row.append('?')
    fog = []
    for j in range(MAP_HEIGHT):
        fog.append(deepcopy(row))

    # TODO: initialize player
    player.clear()
    #   You will probably add other entries into the player dictionary
    player['x'] = 0
    player['y'] = 0
    player['copper'] = 0
    player['silver'] = 0
    player['gold'] = 0
    player['GP'] = 0
    player['day'] = 1
    player['steps'] = 0
    player['total_steps'] = 0
    player['turns'] = TURNS_PER_DAY
    player['pickaxe'] = 1
    player['backpack'] = 10
    player['warehouse'] = [0, 0 ,0]
    player['name'] = ''
    player['portalx'] = 0
    player['portaly'] = 0
    player['torch'] = 3
    player['MAP_WIDTH'] = MAP_WIDTH
    player['MAP_HEIGHT'] = MAP_HEIGHT

    clear_fog(player)

def clear_fog(player):
    global fog
    x = player['x']
    y = player['y']

    difference = math.floor(player['torch'] / 2)
    #Replaces '?' with ' ' in a 3x3 radius
    for i in range(-difference, player['torch'] - difference):
        for j in range(-difference, player['torch'] - difference):
            try:
                #Ensure index is positive as negative index will reference back of the list
                assert y + i >= 0 and x + j >= 0
                
                fog[y + i][x + j] = ' '
            except:
                #Will skip replace when out of index of fog (Trying to replace the edge of map)
                continue
    return

#-------------GAME----------------#
initialize_game(game_map, player)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player['y'] -= 1
            elif event.key == pygame.K_a:
                player['x'] -= 1
            elif event.key == pygame.K_s:
                player['y'] += 1
            elif event.key == pygame.K_d:
                player['x'] += 1

    #Adding ground tile images
    for i in range(MAP_HEIGHT):
        for j in range(MAP_WIDTH):
            if i == 0:
                if j == 0:
                    selectedTile = topLeft
                elif j == MAP_WIDTH - 1:
                    selectedTile = topRight
                else:
                    selectedTile = topMid
            elif i == MAP_HEIGHT - 1:
                if j == 0:
                    selectedTile = botLeft
                elif j == MAP_WIDTH - 1:
                    selectedTile = botRight
                else:
                    selectedTile = botMid
            elif j == 0:
                selectedTile = midLeft
            elif j == MAP_WIDTH - 1:
                selectedTile = midRight
            else:
                selectedTile = mid
            
            position = (MID_SCREENX + ((j - player['x']) * TILE_SIZE[0]), MID_SCREENY + ((i - player['y']) * TILE_SIZE[1]))
            screen.blit(selectedTile, position)
            
    pygame.display.update()
    clock.tick(60)