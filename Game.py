import pygame
from sys import exit

pygame.init() #must have for pygame to run
screen = pygame.display.set_mode((800, 400)) #tab size
pygame.display.set_caption('Game') #title of tab
clock = pygame.time.Clock()
test_font = pygame.font.Font(None, 50)

test_surface = pygame.Surface((100, 200))
test_surface.fill('Red')
#img_surface = pygame.image.load('graphics/Sky.png').convert_alpha()  convert() makes the img easier for python to use. add alpha to remove alpha values
score_surface = test_font.render('Game', True, 'Green')
score_rect = score_surface.get_rect(center = (400,50))
#player_surface = pygame.image.load('file').convert_alpha()
#player_rect = player_surface.get_rect(midbottom = (80,300))  basically sets the reference point

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #pygame.QUIT is the event when the tab 'X' is clicked
            pygame.quit()
            exit() #break technically can but sys.exit() closes all code from any other that is also running
        if event.type == pygame.MOUSEBUTTONUP:
            print('mouse up')
        if event.type == pygame.MOUSEMOTION: #returns a tuple (x, y) when mouse move
            print(event.pos)

    screen.blit(test_surface, (0, 0)) #put surface on main surface
    pygame.draw.rect(screen,'Pink', score_rect, 6, 20) #make 2 if u want the inner fill with border
    pygame.draw.rect(screen,'Pink', score_rect, 0, 20) #shapes at 1.19.09 vid  #the 6 represents border #20 represents rounding radius for corner
    screen.blit(score_surface, score_rect)
    #screen.blit(player_surface, player_rect)
    #player_rect.left += 1  to move right cuz u move the rectangle and the image moves based on the rectangle

    #snail_rect.x -= 4  to move the snail
    #if snail_rect.right < 0: snail_rect.left = 800

    """
    if player_rect.colliderect(snail_rect):  returns 0 or 1. python converts 1 into true and 0 is false
        print('collision')
    mouse_pos = pygame.mouse.get_pos()
    if player_rect.collidepoint((x, y))  (x,y) can be changed with mouse_pos
        print(pygame.mouse.get_pressed())  returns (false, false, false) depending on which mouse key pressed become true
    """

    pygame.display.update() #'refreshes' screen
    clock.tick(60) #ensure that the while loop only loops 60 times per sec