from socket import *
import pygame
import pickle

# VM: 20.199.99.151

# connect to server
clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect(('127.0.0.1', 20000))

# initialize pygame
pygame.init()
screenWidth = 1500
screenHeight = 600

# form the game display window
gameDisplay = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Racing Multiplayer Game')

# load background images
background = 'img/back_ground1.jpg'
car = 'img/car.png'
bgImg = pygame.image.load(background)
carImg = pygame.image.load(car)

# background variables
bg_y1 = 0
bg_y2 = -screenHeight
bg_speed = 3

# car variables
location = [0,0]
car_bottom_offset = 10
car_speed = 1.5

# shows the car for a given road
def showCar(bg_x, location_x, location_y):
    car_x = bg_x + bgImg.get_width()/2 - carImg.get_width()/2 + location_x
    car_y = bgImg.get_height() - carImg.get_height() - car_bottom_offset + location_y
    gameDisplay.blit(carImg, (car_x, car_y))

# shows the road of a given player index
def showMovingRoad(bg_y1, bg_y2, playersCnt, idx):
    bg_x = (screenWidth/2) - playersCnt*(bgImg.get_width()/2) + idx*(bgImg.get_width())
    gameDisplay.blit(bgImg, (bg_x, bg_y1))
    bg_y1 += bg_speed
    gameDisplay.blit(bgImg, (bg_x, bg_y2))
    bg_y2 += bg_speed
    if bg_y1 >= screenHeight:
        bg_y1 = -bgImg.get_height()
    if bg_y2 >= screenHeight:
        bg_y2 = -bgImg.get_height()
    return bg_x, bg_y1, bg_y2

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
        location[0] -= car_speed
    if keys[pygame.K_RIGHT]:
        location[0] += car_speed

    # send the current player location
    clientSock.send(pickle.dumps(location))
    # receive all players
    players = pickle.loads(clientSock.recv(4096))

    # make a new display
    gameDisplay = pygame.display.set_mode((screenWidth, screenHeight))

    for i in range(len(players)):
        # draw the background street for each player
        bg_x, bg_y1, bg_y2 = showMovingRoad(bg_y1, bg_y2, len(players), i)

        # draw each player car
        showCar(bg_x, players[i].location[0], players[i].location[1])
        
    # redraw the scene
    pygame.display.update()