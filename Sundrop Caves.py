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

def update_map(game_map, player):
    #Order of update, P > T > M > ?
    #Adding Portal Stone Coordinates
    game_map[player['portaly']][player['portalx']] = 'P'

    #Adding Town Coordinates
    game_map[0][0] = 'T'

    #Adding Player Coordinates
    game_map[player['y']][player['x']] = 'M'
    return game_map

def draw_view(game_map, player):
    x = player['x']
    y = player['y']

    #Setting row based on viewport radius
    row = {}
    for i in range(player['torch']):
        row[i + 1] = ''

    #Update Map with T,M,P,?
    updated_map = update_map(game_map, player)
    
    difference = math.floor(player['torch'] / 2)
    for i in range(-difference, player['torch'] - difference):
        for j in range(-difference, player['torch'] - difference):
            try:
                #Ensure index is positive as negative index will reference back of the list
                assert y + i >= 0 and x + j >= 0

                #Recording down the grids in the 3x3/5x5 radius
                row[i + (1 + difference)] += updated_map[y + i][x + j]
            except:
                #Will draw # when out of index is negative or out of index (Wall Found)
                row[i + (1 + difference)] += '#'
    return row

def movement(direction, view):
    player['steps'] += 1
    player['total_steps'] += 1

    #Adjusting view based on viewport size
    if player['torch'] == 5:
        diff = 1
    else:
        diff = 0

    if direction == 'w':
        #Move Up
        determine_grid_and_action(1 + diff, 1 + diff, view)

    elif direction == 'a':
        #Move Left
        determine_grid_and_action(2 + diff, 0 + diff, view)

    elif direction == 's':
        #Move Down
        determine_grid_and_action(3 + diff, 1 + diff, view)

    else:
        #Move Right
        determine_grid_and_action(2 + diff, 2 + diff, view)

    clear_fog(player)

def determine_grid_and_action(row, col, view):
    global moving, leftRight, upDown

    #Row (dictionary) - 1, 2, 3
    #Col (string format) - '012'
    '''
    (row, col)
    +-----+-----+-----+     
    | 1,0 | 1,1 | 1,2 |
    +-----+-----+-----+
    | 2,0 | 2,1 | 2,2 |
    +-----+-----+-----+
    | 3,0 | 3,1 | 3,2 |
    +-----+-----+-----+
    '''

    difference = math.floor(player['torch'] / 2)
    #Checks only the viewport and not the whole map when moving
    if view[row][col] == '#':
        print('You ran into the wall.')

    elif view[row][col] == ' ' or view[row][col] == 'P':
        #Move
        game_map[player['y']][player['x']] = ' ' #Remove Previous Location from Gamemap
        moving = True
        determine_updownleftright(col - difference, row - difference - 1)

    #elif view[row][col] == 'T':
    #    game_map[player['y']][player['x']] = ' ' #Remove Previous Location from Gamemap
    #    return_town() #Go back to 'T' goes back town

    elif mineral_names[view[row][col]] not in minerals[0:player['pickaxe']]:
        #Only can mine ores available for the pickaxe lvl
        print(f'Your pickaxe is not good enough to mine {mineral_names[view[row][col]]}.')

    else:
        if calculate_load() != player['backpack']:
            #Move
            game_map[player['y']][player['x']] = ' ' #Remove Previous Location from Gamemap
            moving = True
            determine_updownleftright(col - difference, row - difference - 1)
            game_map[player['y']][player['x']] = ' ' #Remove Ore Mined from gamemap

            #Add Count to the desired ore and only adds up to max load
            ore_count = randint(1, minerals_per_node_max[mineral_names[view[row][col]]])
            adding = min(ore_count, player['backpack'] - calculate_load())
            player[mineral_names[view[row][col]]] += adding
            
            print(f'You mined {ore_count} piece(s) of {mineral_names[view[row][col]]}')
            #Message for overflow load
            if adding != ore_count:
                print(f'...but you can only carry {adding} more piece(s)!')

        else:
            print("You can't carry any more, so you can't go that way.")

def calculate_load():
    count = 0
    count += player['copper']
    count += player['silver']
    count += player['gold']
    return count

def determine_updownleftright(x, y):
    global upDown, leftRight
    if x != 0:
        leftRight = x
    else:
        upDown = y

def portal_stone(tired):
    if tired == True:
        print('You are exhausted.')
    print('You place your portal stone here and zap back to town.')
    game_map[player['portaly']][player['portalx']] = ' ' #Remove old portal stone from map
    player['portalx'], player['portaly'] = player['x'], player['y'] #Set portal stone position
    
    return_town()

def return_town():
    global ore_price
    global game_state
    player['x'], player['y'] = 0, 0
    player['day'] += 1
    ore_price = set_ore_price()
    deposit_ore()
    game_state = 'town'

def set_ore_price():
    copper = randint(*prices['copper'])
    silver = randint(*prices['silver'])
    gold = randint(*prices['gold'])
    return {'copper': copper, 'silver': silver, 'gold': gold}

def sell_ore(copper, silver, gold):
    print('\n------------------------------------------------------')
    total_gp = 0
    
    if copper == True:
        gp = (player['copper'] + player['warehouse'][2]) * ore_price['copper']
        total_gp += gp
        print(f'You sell {player['copper'] + player['warehouse'][2]} copper ore for {gp} GP.')
        player['copper'], player['warehouse'][2] = 0, 0

    if silver == True:
        gp = (player['silver'] + player['warehouse'][1]) * ore_price['silver']
        total_gp += gp
        print(f'You sell {player['silver'] + player['warehouse'][1]} silver ore for {gp} GP.') 
        player['silver'], player['warehouse'][1] = 0, 0

    if gold == True:
        gp = (player['gold'] + player['warehouse'][0]) * ore_price['gold']
        total_gp += gp
        print(f'You sell {player['gold'] + player['warehouse'][0]} gold ore for {gp} GP.')
        player['gold'], player['warehouse'][0] = 0, 0

    if total_gp != 0:
        player['GP'] += total_gp
        print(f'You now have {player['GP']} GP!')
        deposit_ore()

def deposit_ore():
    priority = ['gold', 'silver', 'copper']
    store_amount = 0
    for ores in priority:
        if WAREHOUSE_SIZE - sum(player['warehouse']) <= 0:
            break
        store_amount = min(player[ores], WAREHOUSE_SIZE - sum(player['warehouse']))
        player[ores] -= store_amount
        player['warehouse'][priority.index(ores)] += store_amount
    if store_amount > 0:
        print('You deposited your ores in the warehouse.')

#-------------GAME----------------#
game_state = 'main'
#Player animation variables
moving, upDown, leftRight, cycles, playerAnim = False, 0, 0, 0, charFront[0]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and moving == False and game_state == 'mine':
            keyPressed = pygame.key.name(event.key)
            if keyPressed == 'w' or keyPressed == 'a' or keyPressed == 's' or keyPressed == 'd':
                view = draw_view(game_map, player)
                movement(keyPressed, view)

    screen.fill((0, 0, 0))

    if game_state == 'main':
        show_main_menu()
        choice = input('Your Choice? ').lower()

    if choice == 'n' or game_state == 'town':
        if game_state == 'main':
            #New Game
            initialize_game(game_map, player)
            player['name'] = get_name()
            
        game_state = 'town'
        ore_price = set_ore_price()

    elif choice == 'l':
        #Load Game
        try:
            with open('savefile.json', 'r') as textfile:
                if len(textfile.readlines()) == 0:
                    print('No save data found.')
                else:
                    game_map, fog, player = load_game('savefile.json')
                    game_state = 'town'
                    print('Game loaded.')
        except:
            print("Save file not found. Please create a file 'savefile.json' in the same folder as the game.")
    
    elif choice == 'h':
        try:
            load_highscores('highscores.txt')
        except:
            print("Highscores file not found. Please create a file 'highscores.txt' in the same folder as the game.")

    elif choice == 'q':
        #Quit
        print('Thanks for playing!')
        break

    if game_state == 'town':
        show_town_menu()
        move = input('Your choice? ').lower()
        if move == 'b':
            #Shop
            while True:
                show_shop()
                option = input('Your choice? ').lower()
                if option == 'p' and player['pickaxe'] != 3:
                    #Upgrade Pickaxe
                    if player['GP'] >= pickaxe_price[player['pickaxe'] - 1]:
                        player['GP'] -= pickaxe_price[player['pickaxe'] - 1]
                        player['pickaxe'] += 1
                        print(f'Congratulations! You can now mine {minerals[player['pickaxe'] - 1]}!')
                    else:
                        print('You do not have enough GP!')

                elif option == 'b':
                    #Upgrade Backpack
                    if player['GP'] >= player['backpack'] * 2:
                        player['GP'] -= player['backpack'] * 2
                        player['backpack'] += 2
                        print(f'Congratulations! You can now carry {player['backpack']} items!')
                    else:
                        print('You do not have enough GP!')

                elif option == 'm' and player['torch'] == 3:
                    #Buy magic torch
                    if player['GP'] >= 50:
                        player['GP'] -= 50
                        player['torch'] = 5
                        print(f'Congratulations! You can now view in a 5x5 radius!')
                    else:
                        print('You do not have enough GP!')

                elif option == 'l':
                    print('Bye! See you again!')
                    #Leave
                    break

        elif move == 's':
            #Sell Ores
            while True:
                show_sell_menu()
                sell = input('Your choice? ').lower()
                if sell == 'c' and (player['copper'] + player['warehouse'][2]) != 0:
                    sell_ore(True, False, False)

                elif sell == 's' and (player['silver'] + player['warehouse'][1]) != 0:
                    sell_ore(False, True, False)

                elif sell == 'g' and (player['gold'] + player['warehouse'][0]) != 0:
                    sell_ore(False, False, True)

                elif sell == 'l':
                    print('Bye, See you again! New ore prices daily!')
                    break

                else:
                    #Input Validation
                    print('Please enter a valid choice!')
                
                if player['GP'] >= WIN_GP:
                    game_state = game_end('highscores.txt')
                    break

        elif move == 'i':
            #Display Player Information
            show_information(player)

        elif move == 'm':
            #View Map
            draw_map(game_map, fog, player)

        elif move == 'e':
            player['steps'] = 0
            player['x'], player['y'] = player['portalx'], player['portaly'] #Teleport to portal stone
            clear_fog(player)

            #Enter Mine
            game_state = 'mine'
            print_day()

        elif move == 'v':
            #Save Game
            try:
                save_data = save_game(game_map, fog, player, 'savefile.json')
                print('Game Saved.')
            except:
                print("Save file not found. Please create a file 'savefile.json' in the same folder as the game.")

        elif move == 'q':
            #Back to main menu
            game_state = 'main'
            break

    #Mine Code
    if game_state == 'mine':
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