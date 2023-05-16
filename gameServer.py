from socket import *
import threading

# bind to address and listen to connections
address = '127.0.0.1'
port = 20000
serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind((address, port))
serverSock.listen()

# initializations
clients = []
locationOffsets = []

# thread for each player
def sendClientScene(clientSock):
    while True:
        try:
            # receive the current player movement
            locationOffsets[clients.index(clientSock)] = clientSock.recv(4096).decode()

            # send the number of players
            clientsCnt = str(len(clients))
            clientSock.send(clientsCnt.encode())

            ack = clientSock.recv(1024)

            # send all players' movements
            locations = ','.join(locationOffsets)
            clientSock.send(locations.encode())
            
            ack = clientSock.recv(1024)
        except:
            break

    # remove client from lists if player exits game 
    clientSock.close()
    clients.remove(clientSock)
    locationOffsets.pop(clients.index(clientSock))


while True:
    # wait for a connection
    print('listening to connections...')
    clientSock, (address, port) = serverSock.accept()
    print('connection established')
    
    # add client to lists
    clients.append(clientSock)
    locationOffsets.append('0/0')

    # form a new thread for the client
    thread = threading.Thread(target=sendClientScene, args=(clientSock,))
    thread.start()