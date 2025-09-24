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
text_surface = test_font.render('Game', True, 'Green')

#player_surface = pygame.image.load('file').convert_alpha()
#player_rect = player_surface.get_rect(midbottom = (80,300))  basically sets the reference point

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #pygame.QUIT is the event when the tab 'X' is clicked
            pygame.quit()
            exit() #break technically can but sys.exit() closes all code from any other that is also running

    screen.blit(test_surface, (0, 0)) #put surface on main surface
    screen.blit(text_surface, (300, 50))
    #screen.blit(player_surface, player_rect)
    #player_rect.left += 1  to move right cuz u move the rectangle and the image moves based on the rectangle

    pygame.display.update() #'refreshes' screen
    clock.tick(60) #ensure that the while loop only loops 60 times per sec