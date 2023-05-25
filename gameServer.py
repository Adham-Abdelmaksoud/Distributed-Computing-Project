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
global_leadboard = []



def calculateHighScores(leadboard):
    scores={}
    for player in players:
        scores[player.name]=player.score
    print(scores)
    leadboard = sorted(scores.items(), key = lambda x:x[1], reverse = True)
    print(leadboard)
    return leadboard

# broadcast a message to all players
def broadcast(message):
    for clientSock in clientSocks_chat:
        clientSock.send(message.encode())

# thread for updating database
def updateDB():
    for player in players:
        player.updateScore()
        player.updateLocation()
    threading.Timer(3, updateDB).start()

        

# thread for each player
def sendClientScene(clientSock_game, clientSock_chat, player, global_leadboard):
    while True:
        try:

            #Generate Leadboard according to players scores
            global_leadboard=calculateHighScores(global_leadboard)
            senderables=[players,player.score,global_leadboard]
            
            # receive current player location
            recievables = pickle.loads(clientSock_game.recv(4096))
            player.location = recievables[0]
            player.score = recievables[1]
            # send all players
            clientSock_game.send(pickle.dumps(senderables))

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
        player = Player(nickname, [0,0], 0)
        players.append(player)

        # form a new thread for the client
        playerThread = threading.Thread(target=sendClientScene, args=(clientSock_game, clientSock_chat, player,global_leadboard,))
        playerThread.start()