from socket import *
import pygame
import pickle
import threading
import tkinter
from tkinter import simpledialog
import tkinter.scrolledtext
import queue
import random
from time import sleep


# VM: 20.199.99.151
# serverIP = '20.199.99.151'
serverIP = '127.0.0.1'
serverPort = 20000

# connect to server for game
clientSock_game = socket(AF_INET, SOCK_STREAM)
clientSock_game.connect((serverIP, serverPort))
# connect to server for chat
clientSock_chat = socket(AF_INET, SOCK_STREAM)
clientSock_chat.connect((serverIP, serverPort+20))

# get the nickname from the player
msg = tkinter.Tk()
msg.withdraw()
nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)
clientSock_chat.send(nickname.encode())
print(nickname)

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

# background variables
bg_y1 = 0
bg_y2 = -screenHeight
bg_speed = 2
limit1 = 15
limit2 = bgImg.get_width()-carImg.get_width()-15

# player car variables
location = [0,0]
car_bottom_offset = 10
car_speed = 1

#enemy car variables
random_x = 0
enemy_y = screenHeight
enemy_car_starty2 = -screenHeight
enemy_car_speed = 1
enemy_car_width = 49
enemy_car_height = 10

# score variables
count = 0
white = (255, 255, 255)
black = (0, 0, 0)

# queues
messageQueue = queue.Queue()
textAreaQueue = queue.Queue()

# shows the car for a given road
def showCar(bg_x, location_x, location_y):
    car_x = bg_x + bgImg.get_width()/2 - carImg.get_width()/2 + location_x
    car_y = bgImg.get_height() - carImg.get_height() - car_bottom_offset + location_y
    if car_x < bg_x + limit1:
        car_x = bg_x + limit1
    if car_x > bg_x + limit2:
        car_x = bg_x + limit2
    gameDisplay.blit(carImg, (car_x, car_y))
    return car_x, car_y

#shows the enemy car
def showEnemyCar(bg_x, random_x, enemy_y):
    if enemy_y >= screenHeight:
        enemy_y = -bgImg.get_height()
        random_x = random.randrange(limit1, limit2)
    enemy_x = bg_x + random_x
    gameDisplay.blit(enemyImg, (enemy_x, enemy_y))
    enemy_y += enemy_car_speed
    return random_x, enemy_y

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
        #viewing broadcasted message
        text_area.insert('end',message)
        text_area.yview('end')
        text_area.config(state='disabled')

# view the score
def highscore(count):
    font2 = pygame.font.SysFont("arial", 20)
    text2 = font2.render("Score : " + str(int(count/100)*100), True, white)
    gameDisplay.blit(text2, (0, 0))
    return count

def display_message(msg):
        font = pygame.font.SysFont("comicsansms", 72, True)
        text = font.render(msg, True, (255, 255, 255))
        gameDisplay.blit(text, (600 - text.get_width() // 2, 240 - text.get_height() // 2))
        pygame.display.update()
        sleep(1)

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

    def write():
        chatMessage = f"{nickname}:{input_area.get('1.0','end')}"
        messageQueue.put(chatMessage)
        input_area.delete('1.0','end')

    def stop():
        win.quit()
        clientSock_chat.close()
        exit(0)

    send_button = tkinter.Button(win, text= "Send",command=write)
    send_button.config(font=("Arial",12))
    send_button.pack(padx=20,pady=5)

    win.protocol("WM_DELETE_WINDOW",stop)
    win.mainloop()

# make GUI thread
guiThread = threading.Thread(target=gui)
guiThread.start()

# Game and Chat main thread
run = True
crash = False
iteration=False
while run:
    
    # if the user exits the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    if not run:
        print('Player Logged Out!!')
        pygame.display.quit()
        pygame.quit()
        clientSock_game.close()
        clientSock_chat.close()
        break
    
    # if the user presses arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        location[0] -= car_speed
    if keys[pygame.K_RIGHT]:
        location[0] += car_speed
    senderables = [location,int(count/100)*100]
    
    # send the current player location and score
    clientSock_game.send(pickle.dumps(senderables))

    # receive all players locations
    receivables = pickle.loads(clientSock_game.recv(4096))
    players=receivables[0]

    # if first iteration, receive client's last attempt -score- 
    if not iteration:
        count=receivables[1]
        my_idx=len(players)-1
        iteration=True
        
    # get chat message
    if not messageQueue.empty():
        chatMessage = messageQueue.get()
    else:
        chatMessage = ' '
    clientSock_chat.send(chatMessage.encode())
    broadcastMessage = clientSock_chat.recv(4096).decode()
    broadcastMessage = broadcastMessage.strip()
    broadcastMessage += '\n'
    if broadcastMessage != ' ' and broadcastMessage != '\n':
        text_area = textAreaQueue.get()
        textAreaQueue.put(text_area)
        updateTextArea(text_area, broadcastMessage)


    gameDisplay.fill(list(black))
    for i in range(len(players)):
        # draw the background street for each player
        bg_x, bg_y1, bg_y2 = showMovingRoad(bg_y1, bg_y2, len(players), i)
        # draw each player car
        car_x, car_y = showCar(bg_x, players[i].location[0], players[i].location[1])
        # draw enemy car
        random_x, enemy_y = showEnemyCar(bg_x, random_x, enemy_y)
        enemy_x = bg_x + random_x

        # Saving the values of the current client
        if i == my_idx:
            my_enemy_x= enemy_x
            my_enemy_y= enemy_y
            my_car_x=car_x
            my_car_y=car_y

        # detect collisions for current client only
    if detectCollision(my_car_x, my_car_y, my_enemy_x, my_enemy_y):
        display_message("Game Over")
        count=0
        crash = True
        

    #Displaying score
    if not crash:
        count = highscore(count)
        count += 1
        
    # redraw the scene
    pygame.display.update()