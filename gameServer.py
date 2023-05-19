from socket import *
import threading
import pickle
from player import Player

# bind to address and listen to connections
address = ''
port = 20000
serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind((address, port))
serverSock.listen()

# initializations
clientSocks = []
players = []

# thread for each player
def sendClientScene(clientSock, player):
    while True:
        try:
            # receive current player location
            player.location = pickle.loads(clientSock.recv(4096))
            # send all players
            clientSock.send(pickle.dumps(players))

        except:
            break

    # remove client from lists if player exits game 
    clientSock.close()
    clientSocks.remove(clientSock)
    players.remove(player)


while True:
    # wait for a connection
    print('listening to connections...')
    clientSock, (address, port) = serverSock.accept()
    print('connection established')
    
    # add client to lists
    clientSocks.append(clientSock)
    player = Player([0,0])
    players.append(player)

    # form a new thread for the client
    thread = threading.Thread(target=sendClientScene, args=(clientSock, player,))
    thread.start()