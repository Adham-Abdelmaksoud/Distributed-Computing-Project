from socket import *
import pygame
import pickle
import threading
import tkinter
from tkinter import simpledialog
import tkinter.scrolledtext
import queue

# VM: 20.199.99.151
# serverIP = '20.199.99.151'
serverIP = '127.0.0.1'
serverPort = 20000

# connect to server
clientSock_game = socket(AF_INET, SOCK_STREAM)
clientSock_game.connect((serverIP, serverPort))

clientSock_chat = socket(AF_INET, SOCK_STREAM)
clientSock_chat.connect((serverIP, serverPort+20))

# get the nickname from the player
msg=tkinter.Tk()
msg.withdraw()
nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)
clientSock_chat.send(nickname.encode())
print(nickname)

# initialize pygame
pygame.init()
screenWidth = 1500
screenHeight = 600

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
    if car_x < bg_x + 15:
        car_x = bg_x + 15
    if car_x > bg_x + bgImg.get_width() - carImg.get_width() - 15:
        car_x = bg_x + bgImg.get_width() - carImg.get_width() - 15
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


def updateTextArea(text_area, message):
    if message != ' ':
        text_area.config(state = 'normal')
        #viewing broadcasted message
        text_area.insert('end',message)
        text_area.yview('end')
        text_area.config(state='disabled')


messageQueue = queue.Queue()
textAreaQueue = queue.Queue()
# chat
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
        run_chat= False
        win.destroy()
        clientSock_game.close()
        exit(0)

    send_button = tkinter.Button(win, text= "Send",command=write)
    send_button.config(font=("Arial",12))
    send_button.pack(padx=20,pady=5)

    win.protocol("WM_DELETE_WINDOW",stop)
    win.mainloop()

# GUI thread
guiThread = threading.Thread(target=gui)
guiThread.start()

# form the game display window
gameDisplay = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Racing Multiplayer Game')

# game
run = True
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
        clientSock_game.close()
        break
    
    # if the user presses arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        location[0] -= car_speed
    if keys[pygame.K_RIGHT]:
        location[0] += car_speed


    # send the current player location
    clientSock_game.send(pickle.dumps(location))
    # receive all players
    players = pickle.loads(clientSock_game.recv(4096))


    # get chat message
    if not messageQueue.empty():
        chatMessage = messageQueue.get()
    else:
        chatMessage = ' '
    clientSock_chat.send(chatMessage.encode())
    broadcastMessage = clientSock_chat.recv(4096).decode()
    # broadcastMessage = broadcastMessage.replace(' ', '')
    broadcastMessage = broadcastMessage.strip()
    broadcastMessage += '\n'
    if broadcastMessage != ' ' and broadcastMessage != '\n':
        text_area = textAreaQueue.get()
        textAreaQueue.put(text_area)
        updateTextArea(text_area, broadcastMessage)


    for i in range(len(players)):
        # draw the background street for each player
        bg_x, bg_y1, bg_y2 = showMovingRoad(bg_y1, bg_y2, len(players), i)

        # draw each player car
        showCar(bg_x, players[i].location[0], players[i].location[1])
        
    # redraw the scene
    pygame.display.update()