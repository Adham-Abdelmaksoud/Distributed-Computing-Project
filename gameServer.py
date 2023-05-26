from socket import *
import threading
import pickle
from playerDB import *

# bind to address and listen to connections
IP = ''
PORT = 20000
serverSock_game = socket(AF_INET, SOCK_STREAM)
serverSock_game.bind((IP, PORT))
serverSock_game.listen()

serverSock_chat = socket(AF_INET, SOCK_STREAM)
serverSock_chat.bind((IP, PORT+20))
serverSock_chat.listen()

# initializations
clientSocks_game = []
clientSocks_chat = []
players = []

# broadcast a message to all players
def broadcast(message):
    for clientSock in clientSocks_chat:
        clientSock.send(message.encode())

# thread for updating database
def updateDB():
    for player in players:
        player.updateData()
    threading.Timer(3, updateDB).start()

# thread for each player
def sendClientScene(clientSock_game, clientSock_chat, player):
    while True:
        try:
            # receive current player location
            my_player = pickle.loads(clientSock_game.recv(4096))
            player.crash = my_player.crash
            if not player.crash:
                player.location = my_player.location
                player.score = my_player.score
                player.enemyLocation = my_player.enemyLocation
                player.bg_y = my_player.bg_y
            # send all players
            clientSock_game.send(pickle.dumps(players))

            # receive a message from the player
            message = clientSock_chat.recv(4096).decode()
            # broadcast the message to all players
            broadcast(message)

        except:
            break
    # remove client from lists if player exits game 
    clientSock_game.close()
    clientSock_chat.close()
    clientSocks_game.remove(clientSock_game)
    clientSocks_chat.remove(clientSock_chat)
    players.remove(player)


if __name__ == '__main__':
    updateDB()
    while True:
        # wait for a connection
        print('listening to connections...')
        clientSock_game, (IP, PORT) = serverSock_game.accept()
        clientSock_chat, (IP, PORT) = serverSock_chat.accept()
        print('connection established')

        # get the player nickname
        nickname = clientSock_chat.recv(1024).decode()
        print(f'{nickname} joined the game')

        # add client to lists
        clientSocks_game.append(clientSock_game)
        clientSocks_chat.append(clientSock_chat)

        # create the player
        player = Player(nickname)
        players.append(player)
        clientSock_game.send(pickle.dumps(player))

        # form a new thread for the client
        playerThread = threading.Thread(target=sendClientScene,
                    args=(clientSock_game, clientSock_chat, player,))
        playerThread.start()