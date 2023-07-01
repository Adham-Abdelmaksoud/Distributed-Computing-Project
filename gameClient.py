from socket import *
import pygame
import pickle
import threading
import tkinter
from tkinter import simpledialog, messagebox
import tkinter.scrolledtext
import queue
import random
import sys

isServerLocal = False
if isServerLocal:
    serverIP = '127.0.0.1'
    bg_speed = 3
    car_speed = 2
    enemy_speed_init = 2
    enemy_speed_step = 0.25
else:
    serverIP = '20.199.99.151'
    bg_speed = 20
    car_speed = 20
    enemy_speed_init = 15
    enemy_speed_step = 1.5

serverPort = 50000

# connect to server for game
clientSock_game = socket(AF_INET, SOCK_STREAM)
clientSock_game.connect((serverIP, serverPort))
# connect to server for chat
clientSock_chat = socket(AF_INET, SOCK_STREAM)
clientSock_chat.connect((serverIP, serverPort+20))

# get all previous chat messages
index, messageList, nicknames = pickle.loads(clientSock_chat.recv(4096))

# get the nickname from the player
msg = tkinter.Tk()
msg.withdraw()
while True:
    nickname = simpledialog.askstring("Nickname",
        "   \tPlease choose a nickname\t    ", parent=msg)
    
    # if player closed the nickname window
    if nickname == None:
        clientSock_game.close()
        clientSock_chat.close()
        sys.exit(0)
    
    # if player pressed on OK without entering a nickname
    if nickname == '':
        messagebox.showwarning('Empty String', 'A nickname must be entered!!')
        continue
    elif nickname in nicknames:
        messagebox.showwarning('Used Nickname', 'This nickname is already used!!')
        continue
    else:
        break

clientSock_chat.send(nickname.encode())

# get the player data
my_player = pickle.loads(clientSock_game.recv(8192))
if my_player.enemySpeed == 0:
    my_player.enemySpeed = enemy_speed_init

# initialize pygame and form window
pygame.init()
screenWidth = 1200
screenHeight = 600
gameDisplay = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Racing Multiplayer Game')

# load background images
background = 'img/back_ground1.jpg'
car = 'img/car.png'
enemy = 'img/enemy_car_1.png'
bgImg = pygame.image.load(background)
carImg = pygame.image.load(car)
enemyImg = pygame.image.load(enemy)

# player car variables
car_bottom_offset = 20
newHighscore = False

# colors
white = (255, 255, 255)
gray = (170, 170, 170)
red = (255, 50, 50)
black = (0, 0, 0)
green = (30, 255, 30)

# queues
messageQueue = queue.Queue()
textAreaQueue = queue.Queue()

# shows the car for a given road
def showCar(bg_x, location_x, location_y, name):
    # show the car
    car_x = bg_x + bgImg.get_width()/2 - carImg.get_width()/2 + location_x
    car_y = bgImg.get_height() - carImg.get_height() - car_bottom_offset + location_y
    gameDisplay.blit(carImg, (car_x, car_y))

    # show the player name
    font = pygame.font.SysFont("arial", 17)
    text = font.render(name, True, white)
    name_x = car_x + carImg.get_width()/2
    name_y = car_y + carImg.get_height() + 10
    text_rect = text.get_rect(center=(name_x, name_y))
    gameDisplay.blit(text, text_rect)

    return car_x, car_y

# shows the enemy car
def showEnemyCar(bg_x, random_x, enemy_y, name):
    if enemy_y >= screenHeight:
        enemy_y = -enemyImg.get_height() - 30
        random_x = random.randrange(15, bgImg.get_width()-carImg.get_width()-15)
        if name == my_player.name:
            my_player.enemySpeed += enemy_speed_step
    enemy_x = bg_x + random_x
    gameDisplay.blit(enemyImg, (enemy_x, enemy_y))
    enemy_y += my_player.enemySpeed
    return random_x, enemy_y

# shows the road of a given player index
def showMovingRoad(bg_y1, bg_y2, playersCnt, idx):
    bg_x = (screenWidth/2) - playersCnt*(bgImg.get_width()/2) + idx*(bgImg.get_width())
    gameDisplay.blit(bgImg, (bg_x, bg_y1))
    gameDisplay.blit(bgImg, (bg_x, bg_y2))
    bg_y1 += bg_speed
    bg_y2 += bg_speed
    if bg_y1 >= screenHeight:
        bg_y1 = -bgImg.get_height()
    if bg_y2 >= screenHeight:
        bg_y2 = -bgImg.get_height()
    return bg_x, bg_y1, bg_y2

# detect collision between player and enemy
def detectCollision(car_x, car_y, enemy_x, enemy_y):
    if car_x > enemy_x and car_x < enemy_x+enemyImg.get_width():
        if car_y > enemy_y and car_y < enemy_y+enemyImg.get_height():
            return True
        if car_y+carImg.get_height() > enemy_y and car_y+carImg.get_height() < enemy_y+enemyImg.get_height():
            return True
    if car_x+carImg.get_width() > enemy_x and car_x+carImg.get_width() < enemy_x+enemyImg.get_width():
        if car_y > enemy_y and car_y < enemy_y+enemyImg.get_height():
            return True
        if car_y+carImg.get_height() > enemy_y and car_y+carImg.get_height() < enemy_y+enemyImg.get_height():
            return True
        
    return False

# write a message to the chat text area
def updateTextArea(text_area, message):
    if message != ' ':
        text_area.config(state = 'normal')
        # viewing broadcasted message
        text_area.insert('end',message)
        text_area.yview('end')
        text_area.config(state='disabled')

# view the score
def displayScore(count, highscore):
    font = pygame.font.SysFont("comicsansms", 20)
    # text = font.render("Score : " + str(int(count/100)*100), True, white)
    text_score = font.render("Score : " + str(count), True, white)
    gameDisplay.blit(text_score, (0, 0))

    text_highscore = font.render("Highscore : " + str(highscore), True, white)
    gameDisplay.blit(text_highscore, (0, 40))

# display the game over text
def displayGameOver(bg_x):
    font = pygame.font.SysFont("comicsansms", 40, True)
    text = font.render("Game Over", True, white)
    text_x = bg_x + bgImg.get_width()/2
    text_y = screenHeight/2
    text_rect = text.get_rect(center=(text_x, text_y))
    gameDisplay.blit(text, text_rect)

# display the game over text
def displayNewHighscore(bg_x):
    font = pygame.font.SysFont("comicsansms", 33, True)
    text = font.render("New Highscore!!!", True, green)
    text_x = bg_x + bgImg.get_width()/2
    text_y = screenHeight/2 - 50
    text_rect = text.get_rect(center=(text_x, text_y))
    gameDisplay.blit(text, text_rect)

# display the try again button
def displayTryAgain(bg_x):
    button_width = 180
    button_height = 45
    button_x = bg_x + bgImg.get_width()/2 - button_width/2
    button_y = screenHeight/2 + 40
    button = pygame.Rect(
        button_x,
        button_y,
        button_width,
        button_height
    )
    pygame.draw.rect(gameDisplay, gray, button, border_radius=15)

    text_x = button_x + button_width/2
    text_y = button_y + button_height/2
    font = pygame.font.SysFont('comicsansms', 30, bold=True)
    text = font.render('Try Again', True, red)
    text_rect = text.get_rect(center=(text_x, text_y))
    gameDisplay.blit(text, text_rect)

    return button    

# make a dictionary of all player scores
def calculateScores(players):
    scores = dict()
    for player in players:
        # scores[player.name] = int(player.score/100)*100
        scores[player.name] = player.score
    leaderboard = sorted(scores.items(), key = lambda x:x[1], reverse = True)
    return leaderboard

# display the score leaderboard
def displayLeaderboard(leadboard, color):
    y_coordinate = 80
    font = pygame.font.SysFont("comicsansms", 20)
    text1 = font.render("Leadboard: ", True, white)
    gameDisplay.blit(text1, (0, y_coordinate))
    for name in leadboard:
        y_coordinate += 25
        text2 = font.render(str(name), True, color)
        gameDisplay.blit(text2, (0, y_coordinate))

# GUI thread
def gui():
    win = tkinter.Tk()
    win.configure(bg="lightgray")

    chat_label = tkinter.Label(win, text = "Chat: ", bg= "lightgray")
    chat_label.config(font=("Arial",12))
    chat_label.pack(padx=20, pady=5)

    text_area = tkinter.scrolledtext.ScrolledText(win)
    text_area.pack(padx=20, pady=5)
    text_area.config(state='disabled')
    textAreaQueue.put(text_area)

    msg_label = tkinter.Label(win, text = "Message: ", bg= "lightgray")
    msg_label.config(font=("Arial",12))
    msg_label.pack(padx=20, pady=5)

    input_area = tkinter.Text(win, height = 3)
    input_area.pack(padx=20, pady=5)

    if index != None and messageList != None:
        if index+1 >= len(messageList):
            for message in messageList:
                updateTextArea(text_area, message)
        else:
            i = index+1
            while i != index:
                updateTextArea(text_area, messageList[i])
                i = (i + 1) % 100
            updateTextArea(text_area, messageList[index])

    def write():
        chatMessage = f"{nickname}: {input_area.get('1.0','end')}"
        messageQueue.put(chatMessage)
        input_area.delete('1.0','end')
    def stop():
        win.quit()
        clientSock_game.close()
        clientSock_chat.close()
        exit(0)

    send_button = tkinter.Button(win, text= "Send",command=write)
    send_button.config(font=("Arial",12))
    send_button.pack(padx=20,pady=5)

    win.protocol("WM_DELETE_WINDOW",stop)
    win.mainloop()

# make GUI thread
guiThread = threading.Thread(target=gui, daemon=True)
guiThread.start()

# Game and Chat main thread
run = True
while run:    
    # if the user presses arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        my_player.location[0] -= car_speed
    if keys[pygame.K_RIGHT]:
        my_player.location[0] += car_speed
    if keys[pygame.K_UP]:
        my_player.location[1] -= car_speed
    if keys[pygame.K_DOWN]:
        my_player.location[1] += car_speed

    # limit my player's movement
    if my_player.location[0] < -bgImg.get_width()/2 + carImg.get_width()/2 + 15:
        my_player.location[0] = -bgImg.get_width()/2 + carImg.get_width()/2 + 15
    if my_player.location[0] > bgImg.get_width()/2 - carImg.get_width()/2 - 15:
        my_player.location[0] = bgImg.get_width()/2 - carImg.get_width()/2 - 15
    if my_player.location[1] < -bgImg.get_height() + carImg.get_height() + car_bottom_offset:
        my_player.location[1] = -bgImg.get_height() + carImg.get_height() + car_bottom_offset
    if my_player.location[1] > 0:
        my_player.location[1] = 0

    try:
        # send the current player location
        clientSock_game.send(pickle.dumps(my_player))
        # receive all players
        players = pickle.loads(clientSock_game.recv(4096))
        # send a chat message
        if not messageQueue.empty():
            chatMessage = messageQueue.get()
        else:
            chatMessage = ' '
        clientSock_chat.send(chatMessage.encode())
        # receive the broadcasted message and display it
        broadcastMessage = clientSock_chat.recv(4096).decode()
        broadcastMessage = broadcastMessage.strip()
        broadcastMessage += '\n'
        if broadcastMessage != ' ' and broadcastMessage != '\n':
            text_area = textAreaQueue.get()
            textAreaQueue.put(text_area)
            updateTextArea(text_area, broadcastMessage)
    except:
        break

    # clear the screen
    gameDisplay.fill(list(black))

    # display the leaderboard
    leaderboard = calculateScores(players)
    displayLeaderboard(leaderboard, white)

    for i in range(len(players)):
        # draw the background street for each player
        bg_x, bg_y1, bg_y2 = showMovingRoad(
            players[i].bg_y[0], players[i].bg_y[1], len(players), i
        )
        # draw enemy car
        enemyLocation = showEnemyCar(
            bg_x, players[i].enemyLocation[0], players[i].enemyLocation[1], players[i].name
        )
        absolute_enemy_x = bg_x + enemyLocation[0]
        # draw each player car
        car_x, car_y = showCar(
            bg_x, players[i].location[0], players[i].location[1], players[i].name
        )

        # display gameover
        if players[i].crash:
            displayGameOver(bg_x)

        # display score
        if nickname == players[i].name:
            my_player.location = players[i].location
            my_player.bg_y = [bg_y1, bg_y2]
            my_player.enemyLocation = enemyLocation
            
            displayScore(players[i].score, players[i].highscore)
            my_player.score += 1

            # check if my player collided with the enemy
            if detectCollision(car_x, car_y, absolute_enemy_x, enemyLocation[1]):
                my_player.crash = True

            # display try again button
            if players[i].crash:
                global tryAgainBtn
                tryAgainBtn = displayTryAgain(bg_x)

                if my_player.highscore < players[i].score:
                    newHighscore = True
                    my_player.highscore = players[i].score

                if newHighscore:
                    displayNewHighscore(bg_x)

    for event in pygame.event.get():
        # check if my player exitted the game screen
        if event.type == pygame.QUIT:
            run = False
        # check if my player clicked on try again button
        if my_player.crash == True:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if tryAgainBtn.collidepoint(event.pos):
                    my_player.crash = False
                    my_player.location = [0,0]
                    my_player.enemyLocation = [0,3000]
                    my_player.score = 0
                    my_player.enemySpeed = enemy_speed_init

                    newHighscore = False

    # redraw the scene
    pygame.display.update()

# if the player exitted the game
print('Player Logged Out!!')
pygame.display.quit()
pygame.quit()
clientSock_game.close()
clientSock_chat.close()