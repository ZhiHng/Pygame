import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Sundrop Caves')
clock = pygame.time.Clock()

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
        scaled_tile = pygame.transform.scale(tile, (64, 64))  # Double the size
        tiles.append(scaled_tile)

wall = [tiles[0], tiles[1], tiles[2]]
floorLeft = [tiles[12], tiles[24], tiles[36]]
floorMid = [tiles[13], tiles[25], tiles[37]]
floorRight = [tiles[14], tiles[26], tiles[38]]
groundTiles = [floorLeft, floorMid, floorRight]


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    x=400
    y=200
    for i in range(3):
        for j in range(3):
            screen.blit(groundTiles[j][i],(x,y))
            x += 64
        x -= 192
        y += 64

    pygame.display.update()
    clock.tick(60)