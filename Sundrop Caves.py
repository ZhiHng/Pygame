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
frame_duration_town = 10000
frame_duration_portal = 200
frame_index = 0

gameMain_font = pygame.font.SysFont('ravie', 22)
gameBody_font = pygame.font.SysFont('cooperblack', 20)
cave_background = pygame.transform.scale(pygame.image.load('Assets/Cave.png').convert_alpha(), SCREEN_SIZE)
town_background = pygame.image.load('Assets/Town.png').convert_alpha() #2048 : 1440
changeX = changeY = 0
townX, townY = -400, -200
shop_background = pygame.transform.scale(pygame.image.load('Assets/Shop.png').convert_alpha(), (SCREEN_SIZE[0] * 1.1,SCREEN_SIZE[1] * 1.1))
paper = pygame.transform.scale(pygame.image.load('Assets/Paper.png').convert_alpha(), (262.5,350))
paper.set_colorkey((255, 255, 255))  # Make pure white transparent
paper_rect = paper.get_rect(center = (SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2))
tatteredPaper = pygame.transform.scale(pygame.image.load('Assets/TatteredPaper.png').convert_alpha(), (450,350))
tatteredPaper.set_colorkey((255, 255, 255))  # Make pure white transparent
tatteredPaper_rect = tatteredPaper.get_rect(center = (SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2))
nameInput_surf = pygame.Surface((225,35))
nameInput_surf.fill('White')
nameInput_rect = nameInput_surf.get_rect(center = (400,202))
trans_screen = pygame.Surface((800,400))
trans_screen.fill((0, 0, 0))
transition_speed = 10

#Words blitting
main_words = ['(N)ew Game', '(L)oad Saved Game', '(H)igh Scores', '(Q)uit']
town_words = ['(B)uy Stuff', '(S)ell Ores', 'See Player (I)nformation', '(E)nter Mine', 'Sa(V)e Game', '(Q)uit to Main Menu']
intro2_words = ['You spent all your money to get the deed to a mine, a small','backpack, a simple pickaxe and a magical portal stone.']
intro3_words = ['How quickly can you get the 500 GP you need to retire','and live happily ever after?']
popup_words = []
popup_ticks = []
popup_colour = []
infostatePrev = ''

#Extract tiles from tilemap
tilemap = pygame.image.load('Assets/DwarvenDelve/DwarvenDelve/Background/CaveTilemap.png').convert_alpha()
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
charSheet = pygame.image.load('Assets/DwarvenDelve/DwarvenDelve/Characters/Dwarf/BlueMiner.png').convert_alpha()
charAnims = []
map_width, map_height = charSheet.get_size()
for y in range(0, map_height, 48):
    for x in range(0, map_width, 48):
        rect = pygame.Rect(x, y, 48, 48)
        tile = charSheet.subsurface(rect)
        scaled_tile = pygame.transform.scale(tile, (TILE_SIZE[0]*3,TILE_SIZE[1]*3))
        charAnims.append(scaled_tile)

charFront = [charAnims[0], charAnims[1], charAnims[2], charAnims[3]]
charBack = [charAnims[4], charAnims[5], charAnims[6], charAnims[7]]
charLeft = [pygame.transform.flip(charAnims[8],True,False), pygame.transform.flip(charAnims[9],True,False), pygame.transform.flip(charAnims[10],True,False), pygame.transform.flip(charAnims[11],True,False)]
charRight = [charAnims[8], charAnims[9], charAnims[10], charAnims[11]]
charMineFront = [charAnims[16], charAnims[17], charAnims[18], charAnims[19]]
charMineBack = [charAnims[20], charAnims[21], charAnims[22], charAnims[23]]
charMineLeft = [pygame.transform.flip(charAnims[24],True,False), pygame.transform.flip(charAnims[25],True,False), pygame.transform.flip(charAnims[26],True,False), pygame.transform.flip(charAnims[27],True,False)]
charMineRight = [charAnims[24], charAnims[25], charAnims[26], charAnims[27]]

#Character animations
walkFront = [charFront[0], charFront[1], charFront[0], charFront[3], charFront[0]]
walkBack = [charBack[0], charBack[1], charBack[0], charBack[3], charBack[0]]
walkLeft = [charLeft[0], charLeft[1], charLeft[0], charLeft[3], charLeft[0]]
walkRight = [charRight[0], charRight[1], charRight[0], charRight[3], charRight[0]]
mineFront = [charFront[0], charMineFront[0], charMineFront[1], charMineFront[2], charMineFront[3], charFront[0]]
mineBack = [charBack[0], charMineBack[0], charMineBack[1], charMineBack[2], charMineBack[3], charBack[0]]
mineLeft = [charLeft[0], charMineLeft[0], charMineLeft[1], charMineLeft[2], charMineLeft[3], charLeft[0]]
mineRight = [charRight[0], charMineRight[0], charMineRight[1], charMineRight[2], charMineRight[3], charRight[0]]
idleFront = [charFront[0], charFront[2]]
idleBack = [charBack[0], charBack[2]]
idleLeft = [charLeft[0], charLeft[2]]
idleRight = [charRight[0], charRight[2]]

#Extract ores
copperOre = pygame.transform.scale(pygame.image.load('Assets/DwarvenDelve/DwarvenDelve/Items/CopperOre.png'), TILE_SIZE)
silverOre = pygame.transform.scale(pygame.image.load('Assets/DwarvenDelve/DwarvenDelve/Items/SilverOre.png'), TILE_SIZE)
goldOre = pygame.transform.scale(pygame.image.load('Assets/DwarvenDelve/DwarvenDelve/Items/GoldOre.png'), TILE_SIZE)

fullFog = pygame.Surface(TILE_SIZE)
fullFog.fill((0, 0, 0))
fullFog.set_alpha(150)
halfFog = pygame.Surface(TILE_SIZE)
halfFog.fill((0, 0, 0))
halfFog.set_alpha(100)

#Extract Portal Animation
portalSheet = pygame.image.load('Assets/PORTAL ORANGE-Sheet.png').convert_alpha()
portalAnims = []
map_width, map_height = charSheet.get_size()
for x in range(0, map_width, 64):
    rect = pygame.Rect(x, 0, 64, 64)
    tile = portalSheet.subsurface(rect)
    scaled_tile = pygame.transform.scale(tile, (128,128))
    portalAnims.append(scaled_tile)

#game init
player = {}
game_map = []
fog = []

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
    player['name'] = '' #Max 10 char
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
    global moving, leftRight, upDown, mining, oreMinedX, oreMinedY

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
        popup('You ran into the wall.','Red')
        player['steps'] += 1
        player['total_steps'] += 1

    elif view[row][col] == ' ' or view[row][col] == 'P':
        #Move
        game_map[player['y']][player['x']] = ' ' #Remove Previous Location from Gamemap
        moving = True
        determine_updownleftright(col - difference, row - difference - 1)

    elif view[row][col] == 'T':
        game_map[player['y']][player['x']] = ' ' #Remove Previous Location from Gamemap
        return_town() #Go back to 'T' goes back town

    elif mineral_names[view[row][col]] not in minerals[0:player['pickaxe']]:
        #Only can mine ores available for the pickaxe lvl
        popup(f'Your pickaxe is not good enough to mine {mineral_names[view[row][col]]}.','Red')
        player['steps'] += 1
        player['total_steps'] += 1

    else:
        if calculate_load() != player['backpack']:
            #Move
            game_map[player['y']][player['x']] = ' ' #Remove Previous Location from Gamemap
            mining = True
            determine_updownleftright(col - difference, row - difference - 1)
            oreMinedX, oreMinedY = player['x'] + leftRight, player['y'] + upDown


            #Add Count to the desired ore and only adds up to max load
            ore_count = randint(1, minerals_per_node_max[mineral_names[view[row][col]]])
            adding = min(ore_count, player['backpack'] - calculate_load())
            player[mineral_names[view[row][col]]] += adding
            
            msg = f'You mined {ore_count} piece(s) of {mineral_names[view[row][col]]}'
            #Message for overflow load
            if adding != ore_count:
                msg += f' but you can only carry {adding} more piece(s)!'
            popup(msg,'Blue')

        else:
            popup("You can't carry any more, so you can't go that way.",'Red')
            player['steps'] += 1
            player['total_steps'] += 1
            
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
    global portal
    msg = ''
    if tired == True:
        msg += 'You are exhausted. '
    msg += 'You place your portal stone here and zap back to town.'
    popup(msg,'Blue')
    game_map[player['portaly']][player['portalx']] = ' ' #Remove old portal stone from map
    player['portalx'], player['portaly'] = player['x'], player['y'] #Set portal stone position
    portal = True
    return_town()

def return_town():
    global ore_price
    global transition_state, transition_screen
    player['day'] += 1
    ore_price = set_ore_price()
    deposit_ore()
    transition_screen = transition_speed
    transition_state = 'town'

def set_ore_price():
    copper = randint(*prices['copper'])
    silver = randint(*prices['silver'])
    gold = randint(*prices['gold'])
    return {'copper': copper, 'silver': silver, 'gold': gold}

def sell_ore(copper, silver, gold):
    total_gp = 0
    msg = ''
    if copper == True:
        gp = (player['copper'] + player['warehouse'][2]) * ore_price['copper']
        total_gp += gp
        msg += f'You sell {player['copper'] + player['warehouse'][2]} copper ore for {gp} GP.'
        player['copper'], player['warehouse'][2] = 0, 0

    if silver == True:
        gp = (player['silver'] + player['warehouse'][1]) * ore_price['silver']
        total_gp += gp
        msg += f'You sell {player['silver'] + player['warehouse'][1]} silver ore for {gp} GP.'
        player['silver'], player['warehouse'][1] = 0, 0

    if gold == True:
        gp = (player['gold'] + player['warehouse'][0]) * ore_price['gold']
        total_gp += gp
        msg += f'You sell {player['gold'] + player['warehouse'][0]} gold ore for {gp} GP.'
        player['gold'], player['warehouse'][0] = 0, 0

    if total_gp != 0:
        player['GP'] += total_gp
        msg += f' You now have {player['GP']} GP!'
        popup(msg,'Blue')
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
        popup('You deposited your ores in the warehouse.','Blue')

def show_main_menu(state):
    global screen, game_state, highscore_words
    screen.blit(cave_background, (0,0))
    screen.blit(paper, paper_rect)
    if state == 'main':
        title_surf = gameMain_font.render('Sundrop Caves', True, 'Black')
        title_rect = title_surf.get_rect(center = (400,75))
        screen.blit(title_surf, title_rect)
        for word in main_words:
            body_surf = gameBody_font.render(word, True, 'Black')
            body_rect = body_surf.get_rect(center = (400,150 + 50 * main_words.index(word)))
            screen.blit(body_surf, body_rect)
    elif state == 'highscore':
        title_surf = gameMain_font.render('Highscores', True, 'Black')
        title_rect = title_surf.get_rect(center = (400,75))
        screen.blit(title_surf, title_rect)
        try:
            if highscore_words == []:
                highscore_words = load_highscores('highscores.txt')
            if highscore_words == '~ No Record ~':
                body_surf = gameBody_font.render('~ No Record ~', True, 'Black')
                body_rect = body_surf.get_rect(center = (400,150))
                screen.blit(body_surf, body_rect)
            else:
                for i in range(len(highscore_words)):
                    body_surf = gameBody_font.render(highscore_words[i], True, 'Black')
                    body_rect = body_surf.get_rect(midleft = (290,105 + 25 * i))
                    screen.blit(body_surf, body_rect)
        except:
            popup("Highscores file not found. Please create a file 'highscores.txt' in the game folder.",'Red')
            game_state == 'main'

def show_town_menu(state):
    global screen, townX, townY, current_tick, last_frame_time, frame_duration_town, changeX, changeY, infostatePrev
    screen.blit(town_background, (townX,townY))
    current_tick = pygame.time.get_ticks()
    if current_tick - last_frame_time > frame_duration_town:
        newX, newY = randint(-1, 1)/2, randint(-1, 1)/2
        while newX == changeX or newY == changeY:
            if newX == changeX:
                newX = randint(-1, 1)/2
            if newY == changeY:
                newY = randint(-1, 1)/2
        changeX, changeY = newX, newY
        last_frame_time = current_tick
    townX += changeX
    townY += changeY
    if townX < -2048 or townX > 0:
        townX -= changeX
    if townY < -1440 or townY > 0:
        townY -= changeY

    screen.blit(tatteredPaper, tatteredPaper_rect)
    if infostatePrev == '':
        title_surf = gameMain_font.render('Sundrop Town', True, 'Black')
        title_rect = title_surf.get_rect(center = (400,60))
        screen.blit(title_surf, title_rect)
        title_surf = gameMain_font.render('Day ' + str(player['day']), True, 'Black')
        title_rect = title_surf.get_rect(center = (400,90))
        screen.blit(title_surf, title_rect)
        for word in town_words:
            body_surf = gameBody_font.render(word, True, 'Black')
            body_rect = body_surf.get_rect(center = (400,130 + 40 * town_words.index(word)))
            screen.blit(body_surf, body_rect)

def show_shop(state):
    global screen
    screen.blit(shop_background, (-40,-30))
    screen.blit(tatteredPaper, tatteredPaper_rect)
    title_surf = gameMain_font.render('Shop Menu', True, 'Black')
    title_rect = title_surf.get_rect(center = (400,60))
    screen.blit(title_surf, title_rect)

    shop_words = []

    shop_words.append(f'GP: {player['GP']}')
    if player['pickaxe'] != 3:
        shop_words.append(f'(P)ickaxe upgrade to Level {player['pickaxe'] + 1} to')
        shop_words.append(f'      mine {minerals[player['pickaxe']]} ore for {pickaxe_price[player['pickaxe'] - 1]} GP')
    shop_words.append('(B)ackpack upgrade to carry')
    shop_words.append(f'      {player['backpack'] + 2} items for {player['backpack'] * 2} GP')
    if player['torch'] == 3:
        shop_words.append('(M)agic torch to view a 5x5')
        shop_words.append('      radius in the mines for 50 GP')
    shop_words.append('(L)eave shop')

    for word in shop_words:
        body_surf = gameBody_font.render(word, True, 'Black')
        body_rect = body_surf.get_rect(midleft = (220,80 + 35 * shop_words.index(word)))
        screen.blit(body_surf, body_rect)

def show_information(player, statePrev):
    if statePrev == 'mine':
        screen.blit(tatteredPaper, tatteredPaper_rect)
    title_surf = gameMain_font.render('Player Information', True, 'Black')
    title_rect = title_surf.get_rect(center = (400,60))
    screen.blit(title_surf, title_rect)

    info_wordsLeft = []
    info_wordsRight = []

    info_wordsLeft.append(f'Name: {player['name']}')

    #Show Current position or portal position based on game state
    if game_state == 'mine':
        info_wordsLeft.append(f'Current position: ({player['x']}, {player['y']})')
    else:
        info_wordsLeft.append(f'Portal position: ({player['portalx']} , {player['portaly']})')
    
    info_wordsLeft.append(f'Pickaxe level: {player['pickaxe']} ({minerals[player['pickaxe'] - 1]})')
    info_wordsLeft.append(f'Steps taken: {player['total_steps']}')

    #Show ores if carrying ores
    if calculate_load() != 0:
        info_wordsLeft.append(f'Gold: {player['gold']}')
        info_wordsLeft.append(f'Silver: {player['silver']}')
        info_wordsLeft.append(f'Copper: {player['copper']}')
    
    info_wordsRight.append(f'Day {player['day']}')
    info_wordsRight.append(f'GP: {player['GP']}')
    info_wordsRight.append('Load ')
    info_wordsRight.append(f'{calculate_load()} / {player['backpack']} ')
    info_wordsRight.append('Warehouse ')
    info_wordsRight.append(f'{sum(player['warehouse'])} / {WAREHOUSE_SIZE} ')

    for word in info_wordsLeft:
        body_surf = gameBody_font.render(word, True, 'Black')
        body_rect = body_surf.get_rect(midleft = (220,90 + 40 * info_wordsLeft.index(word)))
        screen.blit(body_surf, body_rect)
    for word in info_wordsRight:
        body_surf = gameBody_font.render(word, True, 'Black')
        body_rect = body_surf.get_rect(midright = (575,90 + 40 * info_wordsRight.index(word)))
        screen.blit(body_surf, body_rect)

def show_sell_menu(state):
    global screen
    screen.blit(shop_background, (-40,-30))
    screen.blit(tatteredPaper, tatteredPaper_rect)
    title_surf = gameMain_font.render('Sell Menu', True, 'Black')
    title_rect = title_surf.get_rect(center = (400,60))
    screen.blit(title_surf, title_rect)

    sell_wordsLeft = []
    sell_wordsRight = []

    sell_wordsLeft.append("Today's Ore Prices")
    
    sell_wordsLeft.append(f'Copper: {ore_price['copper']} GP')
    sell_wordsLeft.append(f'Silver: {ore_price['silver']} GP')
    sell_wordsLeft.append(f'Gold: {ore_price['gold']} GP')
    sell_wordsRight.append("Inventory")
    sell_wordsRight.append(f'Copper: {player['copper'] + player['warehouse'][2]}')
    sell_wordsRight.append(f'Silver: {player['silver'] + player['warehouse'][1]}')
    sell_wordsRight.append(f'Gold: {player['gold'] + player['warehouse'][0]}')
    sell_wordsLeft.append('')
    sell_wordsRight.append(f'GP: {player['GP']}')
    sell_wordsRight.append('')
    sell_wordsRight.append('')
    if player['copper'] + player['warehouse'][2] != 0:
        sell_wordsLeft.append('Sell (C)opper')
    if player['silver'] + player['warehouse'][1] != 0:
        sell_wordsLeft.append('Sell (S)ilver')
    if player['gold'] + player['warehouse'][0] != 0:
        sell_wordsLeft.append('Sell (G)old')
    sell_wordsRight.append('(L)eave')

    for word in sell_wordsLeft:
        body_surf = gameBody_font.render(word, True, 'Black')
        body_rect = body_surf.get_rect(midleft = (220,90 + 33 * sell_wordsLeft.index(word)))
        screen.blit(body_surf, body_rect)
    for word in sell_wordsRight:
        body_surf = gameBody_font.render(word, True, 'Black')
        body_rect = body_surf.get_rect(midright = (575,90 + 33 * sell_wordsRight.index(word)))
        screen.blit(body_surf, body_rect)

# This function saves the game
def save_game(game_map, fog, player, savefile):
    save_data = {}

    # save map
    save_data['game_map'] = deepcopy(game_map)
    # save fog
    save_data['fog'] = deepcopy(fog)
    # save player
    save_data['player'] = deepcopy(player)
    #Write into textfile
    try:
        with open(savefile, 'w') as textfile:
            json.dump(save_data, textfile)
    except:
        raise FileNotFoundError
        
# This function loads the game
def load_game(savefile):
    #Convert textfile into a list
    with open(savefile, 'r') as textfile:
        save_data = json.load(textfile)

        # load map
        game_map = save_data['game_map']
        # load fog
        fog = save_data['fog']
        # load player
        player = save_data['player']

        global MAP_WIDTH
        global MAP_HEIGHT
        MAP_WIDTH = player['MAP_WIDTH']
        MAP_HEIGHT = player['MAP_HEIGHT']
        return game_map, fog, player
    
def load_highscores(highscore_file):
    try:
        with open(highscore_file, 'r') as textfile:
            if len(textfile.readlines()) == 0:
                return '~ No Record ~'
            else:
                #Add data into list
                scores = []
                textfile.seek(0) #Move pointer to start
                for line in textfile:
                    #Days, Name, GP, Steps (List form)
                    scores.append(line.strip().split(','))

                #Arrange in order of top
                scores.sort(key=lambda x: (int(x[0]), int(x[3]), -int(x[2])))

                #Delete the rest not top 5
                if len(scores) > 5:
                    scores.pop(-1)
                    with open(highscore_file, 'w') as file:
                        for item in scores:
                            file.write(item[0] + ',' + item[1] + ',' + item[2] + ',' + item[3] + '\n')
                highscore_words = []
                count = 1
                for item in scores:
                    highscore_words.append(f'{count}. {item[1]}: {item[0]} Days,')
                    highscore_words.append(f'    {item[3]} Steps, {item[2]} GP.')
                    count += 1
                return highscore_words
    except:
        raise FileNotFoundError

def game_end(highscore_file):
    global transition_screen, transition_state
    if transition_screen == 0:
        print('-------------------------------------------------------------')
        print(f'Woo-hoo! Well done, {player['name']}, you have {player['GP']} GP!')
        print('You now have enough to retire and play video games every day.')
        print(f'And it only took you {player['day']} days and {player['total_steps']} steps! You win!')
        print('-------------------------------------------------------------')
        try:
            with open(highscore_file, 'a') as textfile:
                textfile.write(str(player['day']) + ',' + player['name'] + ',' + str(player['GP']) + ',' + str(player['total_steps']) + '\n')
        except:
            popup("Highscores file not found. Please create a file 'highscores.txt' in the game folder.",'Red')
            print('Your score was not recorded.')

    transition_screen = transition_speed
    transition_state = 'main'

def popup(word, colour):
    global popup_words, popup_ticks, popup_colour
    popup_words.append(word)
    popup_ticks.append(0)
    popup_colour.append(colour)

#-------------GAME----------------#
game_state = 'main'
action = choice = move = option = sell = key = ''
name = ''
highscore_words = []
#Player animation variables
moving, mining, upDown, leftRight, cycles, playerAnim = False, False, 0, 0, 0, charFront[0]
transition_screen, transition_opacity, transition_state = 0, 0, ''
portal = False


while True:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if transition_screen == 0:
                if game_state == 'name':
                    if event.key == pygame.K_BACKSPACE:
                        key = 'backspace'
                    elif event.key == pygame.K_RETURN:
                        key = 'enter'
                    elif event.unicode and event.unicode.isprintable():
                        key = event.unicode
                else:
                    keyPressed = pygame.key.name(event.key).lower()
                    if keyPressed == 'i' and infostatePrev != '':
                        infostatePrev = ''
                    elif (keyPressed == 'w' or keyPressed == 'a' or keyPressed == 's' or keyPressed == 'd' or keyPressed == 'i' or keyPressed == 'p' or keyPressed == 'q') and game_state == 'mine' and infostatePrev == '':
                        action = keyPressed
                    elif (keyPressed == 'n' or keyPressed == 'l' or keyPressed == 'h' or keyPressed == 'q') and game_state == 'main':
                        choice = keyPressed
                    elif (keyPressed == 'b' or keyPressed == 's' or keyPressed == 'i' or keyPressed == 'e' or keyPressed == 'v' or keyPressed == 'q') and game_state == 'town':
                        move = keyPressed
                    elif (keyPressed == 'p' or keyPressed == 'b' or keyPressed == 'm' or keyPressed == 'l') and game_state == 'shop':
                        option = keyPressed
                    elif (keyPressed == 'c' or keyPressed == 's' or keyPressed == 'g' or keyPressed == 'l') and game_state == 'sell':
                        sell = keyPressed
                    elif keyPressed == 'h' and game_state == 'highscore':
                        game_state = 'main'
                        highscore_words = []
                    elif keyPressed == 'o':
                        popup("Save file not found. Please create a file 'savefile.json' in the game folder.",'Red')

    if game_state == 'main':
        show_main_menu(game_state)
        if choice == 'n':
            #New Game
            initialize_game(game_map, player)
            name = ''
            transition_screen = transition_speed
            transition_state = '1'
            ore_price = set_ore_price()

        elif choice == 'l':
            #Load Game
            try:
                with open('savefile.json', 'r') as textfile:
                    if len(textfile.readlines()) == 0:
                        popup('No save data found.','Red')
                    else:
                        game_map, fog, player = load_game('savefile.json')
                        transition_screen = transition_speed
                        transition_state = 'town'
                        ore_price = set_ore_price()
                        popup('Game loaded.','Green')
            except:
                popup("Save file not found. Please create a file 'savefile.json' in the folder.",'Red')
        
        elif choice == 'h':
            game_state = 'highscore'

        elif choice == 'q':
            #Quit
            print('Thanks for playing!')
            pygame.quit()
            exit()

        choice = ''

    if game_state == 'name':
        if key != '':
            if key == 'backspace' and len(name) > 0:
                name = name[:-1]
            elif key == 'enter':
                player['name'] = name
                popup(f'Pleased to meet you, {name}. Welcome to Sundrop Town!','coral')
                transition_screen = transition_speed
                transition_state = 'town'
            elif len(name) < 10 and key != 'backspace' and key != 'enter':
                name += key

        screen.blit(paper, paper_rect)

        nameMain_words = []
        nameMain_words.append('Greetings, miner!')
        nameMain_words.append('What is your name?')
        for word in nameMain_words:
            main_surf = gameBody_font.render(word, True, 'Black')
            main_rect = main_surf.get_rect(center = (400,110 + 30 * nameMain_words.index(word)))
            screen.blit(main_surf, main_rect)

        pygame.draw.rect(screen,'White', nameInput_rect, 0, 20)
        pygame.draw.rect(screen,'Black', nameInput_rect, 6, 20)
        
        body_surf = gameBody_font.render(name, True, 'Blue')
        body_rect = body_surf.get_rect(center = (400,200))
        screen.blit(body_surf, body_rect)

        key = ''

    if game_state == 'highscore':
        show_main_menu(game_state)

    if game_state == 'town':
        show_town_menu(game_state)
        if move == 'b':
            transition_screen = transition_speed
            transition_state = 'shop'

        elif move == 's':
            transition_screen = transition_speed
            transition_state = 'sell'

        elif move == 'i':
            #Display Player Information
            infostatePrev = 'town'

        elif move == 'e':
            player['steps'] = 0
            player['x'], player['y'] = player['portalx'], player['portaly'] #Teleport to portal stone
            clear_fog(player)

            #Enter Mine
            transition_screen = transition_speed
            transition_state = 'mine'

        elif move == 'v':
            #Save Game
            try:
                save_data = save_game(game_map, fog, player, 'savefile.json')
                popup('Game Saved.','Green')
            except:
                popup("Save file not found. Please create a file 'savefile.json' in the game folder.",'Red')

        elif move == 'q':
            #Back to main menu
            transition_screen = transition_speed
            transition_state = 'main'

        move = ''

    #Shop
    if game_state == 'shop':
        show_shop(game_state)
        if option == 'p' and player['pickaxe'] != 3:
            #Upgrade Pickaxe
            if player['GP'] >= pickaxe_price[player['pickaxe'] - 1]:
                player['GP'] -= pickaxe_price[player['pickaxe'] - 1]
                player['pickaxe'] += 1
                popup(f'Congratulations! You can now mine {minerals[player['pickaxe'] - 1]}!','Blue')
            else:
                popup('You do not have enough GP!','Red')

        elif option == 'b':
            #Upgrade Backpack
            if player['GP'] >= player['backpack'] * 2:
                player['GP'] -= player['backpack'] * 2
                player['backpack'] += 2
                popup(f'Congratulations! You can now carry {player['backpack']} items!','Blue')
            else:
                popup('You do not have enough GP!','Red')

        elif option == 'm' and player['torch'] == 3:
            #Buy magic torch
            if player['GP'] >= 50:
                player['GP'] -= 50
                player['torch'] = 5
                popup(f'Congratulations! You can now view in a 5x5 radius!','Blue')
            else:
                popup('You do not have enough GP!','Red')

        elif option == 'l':
            popup('Bye! See you again!','Blue')
            #Leave
            transition_screen = transition_speed
            transition_state = 'town'

        option = ''

    #Sell Ores
    if game_state == 'sell':
        show_sell_menu(game_state)
        if sell == 'c' and (player['copper'] + player['warehouse'][2]) != 0:
            sell_ore(True, False, False)

        elif sell == 's' and (player['silver'] + player['warehouse'][1]) != 0:
            sell_ore(False, True, False)

        elif sell == 'g' and (player['gold'] + player['warehouse'][0]) != 0:
            sell_ore(False, False, True)

        elif sell == 'l':
            popup('Bye, See you again! New ore prices daily!','Blue')
            transition_screen = transition_speed
            transition_state = 'town'
        
        if player['GP'] >= WIN_GP:
            game_end('highscores.txt')
        
        sell = ''

    #Mine Code
    if game_state == 'mine':
        if moving == False and mining == False:
            if action == 'w' or action == 'a' or action == 's' or action == 'd':
                view = draw_view(game_map, player)
                movement(action, view)
                if player['steps'] == player['turns']:
                    portal_stone(True)

            elif action == 'i':
                #View Information
                infostatePrev = 'mine'

            elif action == 'p':
                #Use Portal Stone
                portal_stone(False)

            elif action == 'q':
                #Quit to main menu
                transition_screen = transition_speed
                transition_state = 'main'

        action = ''

        #Animations
        if mining == True:
            cycles += 1
            if upDown != 0:
                if upDown == 1:
                    if cycles % 4 == 0 and cycles != 0:
                        playerAnim = mineFront[int((cycles / 4) - 1) % 6]
                else:
                    if cycles % 4 == 0 and cycles != 0:
                        playerAnim = mineBack[int((cycles / 4) - 1) % 6]       
            else:
                if leftRight == 1:
                    if cycles % 4 == 0 and cycles != 0:
                        playerAnim = mineRight[int((cycles / 4) - 1) % 6] 
                else:
                    if cycles % 4 == 0 and cycles != 0:
                        playerAnim = mineLeft[int((cycles / 4) - 1) % 6] 

            if cycles == 48:
                mining = False
                moving = True
                cycles = 0
                game_map[oreMinedY][oreMinedX] = ''

        elif moving == True:
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
                player['steps'] += 1
                player['total_steps'] += 1

        else:
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

        screen.blit(playerAnim, (MID_SCREENX - TILE_SIZE[0],MID_SCREENY - TILE_SIZE[1] - TILE_SIZE[1] / 8))

        if portal == True:
            current_tick = pygame.time.get_ticks()
            if current_tick - last_frame_time > frame_duration_portal:
                frame_index = (frame_index + 1) % len(portalAnims)
                last_frame_time = current_tick
            screen.blit(portalAnims[frame_index], (MID_SCREENX - TILE_SIZE[0] / 1.5, MID_SCREENY - TILE_SIZE[1]))

    if infostatePrev != '':
        show_information(player, infostatePrev)               

    #Intro
    if game_state == '1':
        if transition_opacity == 0:
            transition_screen = 1
            transition_state = '2'
        title_surf = gameMain_font.render('Welcome to Sundrop Caves!', True, 'Orange')
        title_rect = title_surf.get_rect(center = (400,200))
        screen.blit(title_surf, title_rect)

    if game_state == '2':
        if transition_opacity == 0:
            transition_screen = 0.75
            transition_state = '3'
        for word in intro2_words:
            body_surf = gameBody_font.render(word, True, 'Orange')
            body_rect = body_surf.get_rect(center = (400,175 + 50 * intro2_words.index(word)))
            screen.blit(body_surf, body_rect)

    if game_state == '3':
        if transition_opacity == 0:
            transition_screen = 0.75
            transition_state = 'name'
        for word in intro3_words:
            body_surf = gameBody_font.render(word, True, 'Orange')
            body_rect = body_surf.get_rect(center = (400,175 + 50 * intro3_words.index(word)))
            screen.blit(body_surf, body_rect)
    #Intro

    if transition_screen != 0:
        transition_opacity += transition_screen
        trans_screen.set_alpha(transition_opacity)
        screen.blit(trans_screen, (0,0))
        if transition_opacity >= 255:
            transition_screen = -transition_speed
            game_state = transition_state
            if transition_state == 'town':
                player['x'], player['y'] = 0, 0
                portal = False
            transition_state = ''
        if transition_screen == -transition_speed and transition_opacity <= 0:
            transition_screen = 0
            transition_opacity = 0

    if len(popup_words) != 0:
        for i in range(len(popup_words) - 1, -1, -1):
            body_surf = gameBody_font.render(popup_words[i], True, popup_colour[i])
            body_rect = body_surf.get_rect(center = (400, popup_ticks[i] / 4 + 70))
            body_surf.set_alpha(255 - popup_ticks[i] * 1.5)
            popup_ticks[i] += 1
            if popup_ticks[i] * 1.5 >= 255:
                popup_words.pop(i)
                popup_ticks.pop(i)
                popup_colour.pop(i)
            screen.blit(body_surf, body_rect)

    pygame.display.update()
    clock.tick(60)