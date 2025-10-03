import pygame
from sys import exit
from random import randint
from copy import deepcopy
import json
import math

#pygame init
pygame.init()
TILE_SIZE = (48, 48)
SCREEN_SIZE = (800, 400)
MID_SCREENX = SCREEN_SIZE[0] / 2 - TILE_SIZE[0] / 2
MID_SCREENY = SCREEN_SIZE[1] / 2 - TILE_SIZE[1] / 2
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Sundrop Caves')
clock = pygame.time.Clock()

last_frame_time = 0
frame_duration = 300
frame_index = 0

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

#Extract characters
charSheet = pygame.image.load('DwarvenDelve/DwarvenDelve/Characters/Dwarf/BlueMiner.png').convert_alpha()
charAnims = []
map_width, map_height = charSheet.get_size()
for y in range(0, map_height, TILE_HEIGHT):
    for x in range(0, map_width, TILE_WIDTH):
        rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
        tile = charSheet.subsurface(rect)
        scaled_tile = pygame.transform.scale(tile, TILE_SIZE)  # Double the size
        charAnims.append(scaled_tile)

charFront = [charAnims[13], charAnims[16], charAnims[19], charAnims[22]]
charBack = [charAnims[49], charAnims[52], charAnims[55], charAnims[58]]
charLeft = [pygame.transform.flip(charAnims[85],True,False), pygame.transform.flip(charAnims[88],True,False), pygame.transform.flip(charAnims[91],True,False), pygame.transform.flip(charAnims[94],True,False)]
charRight = [charAnims[85], charAnims[88], charAnims[91], charAnims[94]]

#Character animations
walkFront = [charFront[0], charFront[1], charFront[0], charFront[3], charFront[0]]
walkBack = [charBack[0], charBack[1], charBack[0], charBack[3], charBack[0]]
walkLeft = [charLeft[0], charLeft[1], charLeft[0], charLeft[3], charLeft[0]]
walkRight = [charRight[0], charRight[1], charRight[0], charRight[3], charRight[0]]
idleFront = [charFront[0], charFront[2]]
idleBack = [charBack[0], charBack[2]]
idleLeft = [charLeft[0], charLeft[2]]
idleRight = [charRight[0], charRight[2]]

#Extract ores
copperOre = pygame.transform.scale(pygame.image.load('DwarvenDelve/DwarvenDelve/Items/CopperOre.png'), TILE_SIZE)
silverOre = pygame.transform.scale(pygame.image.load('DwarvenDelve/DwarvenDelve/Items/SilverOre.png'), TILE_SIZE)
goldOre = pygame.transform.scale(pygame.image.load('DwarvenDelve/DwarvenDelve/Items/GoldOre.png'), TILE_SIZE)

fullFog = pygame.Surface(TILE_SIZE)
fullFog.fill((0, 0, 0))
fullFog.set_alpha(150)
halfFog = pygame.Surface(TILE_SIZE)
halfFog.fill((0, 0, 0))
halfFog.set_alpha(100)

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
#Player animation variables
moving, upDown, leftRight, cycles, playerAnim = False, 0, 0, 0, charFront[0]

while True:
    if moving == True:
        cycles += 1
        if upDown != 0:
            player['y'] += upDown * 0.05
            if upDown == 1:
                if cycles % 4 == 0 and cycles != 0:
                    playerAnim = walkFront[int((cycles / 4) - 1)] 
            else:
                if cycles % 4 == 0 and cycles != 0:
                    playerAnim = walkBack[int((cycles / 4) - 1)]       
        else:
            player['x'] += leftRight * 0.05
            if leftRight == 1:
                if cycles % 4 == 0 and cycles != 0:
                    playerAnim = walkRight[int((cycles / 4) - 1)] 
            else:
                if cycles % 4 == 0 and cycles != 0:
                    playerAnim = walkLeft[int((cycles / 4) - 1)]  
        
        if cycles == 20:
            moving = False
            upDown = 0
            leftRight = 0
            cycles = 0
            player['x'], player['y'] = round(player['x']), round(player['y'])
            clear_fog(player)
    else:
        if moving == False:
            current_tick = pygame.time.get_ticks()
            if current_tick - last_frame_time > frame_duration:
                if playerAnim in walkFront:
                    idle = idleFront
                elif playerAnim in walkBack:
                    idle = idleBack
                elif playerAnim in walkLeft:
                    idle = idleLeft
                elif playerAnim in walkRight:
                    idle = idleRight
                frame_index = (frame_index + 1) % len(idle)
                last_frame_time = current_tick
                playerAnim = idle[frame_index]


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and moving == False:
            if event.key == pygame.K_w:
                moving = True
                upDown = -1
            elif event.key == pygame.K_a:
                moving = True
                leftRight = -1
            elif event.key == pygame.K_s:
                moving = True
                upDown = 1
            elif event.key == pygame.K_d:
                moving = True
                leftRight = 1

    screen.fill((0, 0, 0))
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

            tileX = MID_SCREENX + ((j - player['x']) * TILE_SIZE[0])
            tileY = MID_SCREENY + ((i - player['y']) * TILE_SIZE[1])

            #Will not blit those out of screen
            if tileX < 0 - TILE_SIZE[0] or tileX > SCREEN_SIZE[0] + TILE_SIZE[0] or tileY < 0 - TILE_SIZE[1] or tileY > SCREEN_SIZE[1] + TILE_SIZE[1]:
                continue

            position = (round(tileX), round(tileY))
            screen.blit(selectedTile, position)

            #blit ores
            if game_map[i][j] == 'C':
                screen.blit(copperOre, position)
            elif game_map[i][j] == 'S':
                screen.blit(silverOre, position)
            elif game_map[i][j] == 'G':
                screen.blit(goldOre, position)

            #blit fog
            
            vision = math.floor(player['torch'] / 2)
            if fog[i][j] == '?':
                screen.blit(selectedTile, position) #remove any ores not discovered
                screen.blit(fullFog, position)
            elif abs(i - player['y']) > vision or abs(j - player['x']) > vision:
                screen.blit(halfFog, position)

            if i == 0:
                if j % 3 == 0:
                    wallTile = wall[2]
                elif j % 2 == 0:
                    wallTile = wall[1]
                else:
                    wallTile = wall[0]
                screen.blit(wallTile, (round(tileX), round(tileY - TILE_SIZE[1])))

    screen.blit(playerAnim, (MID_SCREENX,MID_SCREENY - TILE_SIZE[1] / 8))
            
    pygame.display.update()
    clock.tick(60)