from socket import *
import threading
import pickle
from playerDB import *
from datetime import datetime
import logging

# bind to address and listen to connections
IP = ''
PORT = 20000
serverSock_game = socket(AF_INET, SOCK_STREAM)
# serverSock_game.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSock_game.bind((IP, PORT))
serverSock_game.listen()

serverSock_chat = socket(AF_INET, SOCK_STREAM)
# serverSock_chat.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSock_chat.bind((IP, PORT+20))
serverSock_chat.listen()

# initializations
clientSocks_game = []
clientSocks_chat = []
players = []

# lock
playerLock = threading.Lock()

# logging
logging.basicConfig(level=logging.DEBUG, filename='log.txt', filemode='w')

# get nicknames of players in all rooms
def getPlayersNicknames():
    nicknames = []
    playerLock.acquire()
    for room in players:
        for player in room:
            nicknames.append(player.name)
    playerLock.release()
    return nicknames

# broadcast a message to all players
def broadcast(message):
    for clientSock in clientSocks_chat:
        clientSock.send(message.encode())

# thread for updating database
def updateDB():
    playerLock.acquire()
    for room in players:
        for player in room:
            player.updateData()
    playerLock.release()
    
    synchronizeDBs()
    threading.Timer(1, updateDB).start()

# thread for each player
def sendClientScene(clientSock_game, clientSock_chat, player, room):
    while True:
        try:
            clientSock_game.settimeout(10)
            clientSock_chat.settimeout(10)

            # receive current player location
            my_player = pickle.loads(clientSock_game.recv(4096))
            player.crash = my_player.crash
            player.highscore = my_player.highscore
            if not player.crash:
                player.location = my_player.location
                player.score = my_player.score
                player.enemyLocation = my_player.enemyLocation
                player.bg_y = my_player.bg_y
                player.enemySpeed = my_player.enemySpeed
            # send all players
            clientSock_game.send(pickle.dumps(players[room]))

            # receive a message from the player
            message = clientSock_chat.recv(4096).decode()
            message = message.strip()
            message += '\n'
            if message != ' ' and message != '\n':
                addNewMessage(message)
            # broadcast the message to all players
            broadcast(message)
        except:
            break

    # remove client from lists if player exits game
    clientSock_game.close()
    clientSock_chat.close()
    clientSocks_game.remove(clientSock_game)
    clientSocks_chat.remove(clientSock_chat)

    playerLock.acquire()
    players[room].remove(player)
    playerLock.release()

print(f'Server started at {datetime.now()}')
logging.warning(f'Server started at {datetime.now()}')

if __name__ == '__main__':
    updateDB()
    serverSock_game.settimeout(900)
    serverSock_chat.settimeout(900)
    while True:
        try:
            # wait for a connection
            print('\nlistening to connections...')
            logging.warning('listening to connections...')
            clientSock_game, (IP, PORT) = serverSock_game.accept()
            clientSock_chat, (IP, PORT) = serverSock_chat.accept()
            print(f'connection established with IP:{IP} and port:{PORT}')
            logging.warning(f'connection established with IP:{IP} and port:{PORT}')
        except KeyboardInterrupt:
            break
        except:
            continue

        # get the message list from the database
        try:
            msgIndex, messageList = getAllMessages()
        except:
            logging.exception('Database Message Fetching Error!!')
            clientSock_game.close()
            clientSock_chat.close()
            continue

        if messageList == None:
            messageList = []

        # get the list of nicknames in all rooms
        nicknames = getPlayersNicknames()

        # send the data to the 
        try:
            clientSock_chat.send(pickle.dumps([msgIndex, messageList, nicknames]))
        except:
            logging.exception('Abnormal Behaviour During Send')
            clientSock_game.close()
            clientSock_chat.close()
            continue

        # get the player nickname
        try:
            nickname = clientSock_chat.recv(1024).decode()
            if nickname == '':
                raise ValueError('Empty Nickname Received')
        except:
            print('Server Receiving Error!!')
            logging.exception('Server Receiving Error!!')
            clientSock_game.close()
            clientSock_chat.close()
            continue
        print(f'{nickname} joined the game')
        logging.warning(f'{nickname} joined the game')

        # create the player and add him to a room
        try:
            player = Player(nickname)
        except:
            logging.exception('Database Player Fetching Error!!')
            clientSock_game.close()
            clientSock_chat.close()
            continue

        room = -1
        if len(players) == 0:
            players.append([player])
            room = 0
        else:
            for i in range(len(players)):
                if len(players[i]) < 3:
                    players[i].append(player)
                    room = i
                    break
                if i == len(players)-1:
                    players.append([player])
                    room = i+1

        try:
            clientSock_game.send(pickle.dumps(player))
        except:
            logging.exception('Abnormal Behaviour During Send')
            clientSock_game.close()
            clientSock_chat.close()
            continue

        # add client to lists
        clientSocks_game.append(clientSock_game)
        clientSocks_chat.append(clientSock_chat)

        # form a new thread for the client
        playerThread = threading.Thread(target=sendClientScene, daemon=True,
                    args=(clientSock_game, clientSock_chat, player, room,))
        playerThread.start()
        print('thread created')
        logging.warning('Thread created')

print(f'\nServer closed at {datetime.now()}')
logging.warning(f'Server closed at {datetime.now()}')
serverSock_game.close()
serverSock_chat.close()