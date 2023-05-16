from socket import *
import pygame
from PIL import Image

# connect to server
clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect(('127.0.0.1', 20000))

# initialize pygame
pygame.init()
screenWidth = 1500
screenHeight = 600

# load background images
background = 'img/back_ground1.jpg'
car = 'img/car.png'
bgImg = Image.open(background)
carImg = Image.open(car)
gameBgImg = pygame.image.load(background)
gameCarImg = pygame.image.load(car)

# background variables
bg_y1 = 0
bg_y2 = -600
bg_speed = 3

# car variables
car_offset_x = 0
car_offset_y = 0
car_bottom_offset = 10
car_speed = 1.5

run = True
while run:
    # if the user exits the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    if not run:
        print('Player Logged Out!!')
        clientSock.close()
        break
    
    # if the user presses arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        car_offset_x -= car_speed
    if keys[pygame.K_RIGHT]:
        car_offset_x += car_speed
    
    # send my car movement to the server
    clientSock.send(f'{car_offset_x}/{car_offset_y}'.encode())
    # receive the number of current players from the server
    clientsCnt = int(clientSock.recv(4096).decode())
    clientSock.send(b'ack')
    # receive all cars' movement from the server
    locationOffsets = clientSock.recv(4096).decode().split(',')
    clientSock.send(b'ack')

    # form the game display window
    gameDisplay = pygame.display.set_mode((screenWidth, screenHeight))
    pygame.display.set_caption('Racing Multiplayer Game')

    for i in range(clientsCnt):
        # draw the background street for each player
        bg_x = (screenWidth/2) - clientsCnt*(bgImg.size[0]/2) + i*(bgImg.size[0])
        gameDisplay.blit(gameBgImg, (bg_x, bg_y1))
        bg_y1 += bg_speed
        gameDisplay.blit(gameBgImg, (bg_x, bg_y2))
        bg_y2 += bg_speed
        if bg_y1 >= screenHeight:
            bg_y1 = -bgImg.size[1]
        if bg_y2 >= screenHeight:
            bg_y2 = -bgImg.size[1]

        # draw each player car
        offset_x, offset_y = list(map(float, locationOffsets[i].split('/')))
        car_x = bg_x + bgImg.size[0]/2 - carImg.size[0]/2 + offset_x
        car_y = bgImg.size[1] - carImg.size[1] - car_bottom_offset + offset_y
        gameDisplay.blit(gameCarImg, (car_x, car_y))
        
    # redraw the scene
    pygame.display.update()