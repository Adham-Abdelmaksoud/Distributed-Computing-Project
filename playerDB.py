import pyrebase
import time

config1 = {
    'apiKey': "AIzaSyBke2h_fJ5foz1WJaEKtdfeLWeYDfZa92I",
    'authDomain': "multiplayer-racing-game-c5c89.firebaseapp.com",
    'databaseURL': "https://multiplayer-racing-game-c5c89-default-rtdb.europe-west1.firebasedatabase.app",
    'projectId': "multiplayer-racing-game-c5c89",
    'storageBucket': "multiplayer-racing-game-c5c89.appspot.com",
    'messagingSenderId': "77048992078",
    'appId': "1:77048992078:web:b2932403156e1f259bce1f",
    'measurementId': "G-XDR0MSTT9C"
}
config2 = {
  'apiKey': "AIzaSyCioig00Mzj6E4-MH1PiwZfrSvoVsARVT8",
  'authDomain': "multiplayer-racing-game-86c8f.firebaseapp.com",
  'databaseURL': "https://multiplayer-racing-game-86c8f-default-rtdb.europe-west1.firebasedatabase.app",
  'projectId': "multiplayer-racing-game-86c8f",
  'storageBucket': "multiplayer-racing-game-86c8f.appspot.com",
  'messagingSenderId': "851414683145",
  'appId': "1:851414683145:web:a889c933e73f37e14fb2d8",
  'measurementId': "G-R93M2PM59Y"
}
firebase1 = pyrebase.initialize_app(config1)
firebase2 = pyrebase.initialize_app(config2)
database1 = firebase1.database()
database2 = firebase2.database()


def getAllMessages():
    try:
        index1 = database1.child('Messages').child('index').get().val()
        messageList1 = database1.child('Messages').child('messageList').get().val()
        lastModified1 = database1.child('LastModified').get().val()
    except:
        index1 = database2.child('Messages').child('index').get().val()
        messageList1 = database2.child('Messages').child('messageList').get().val()
        lastModified1 = database2.child('LastModified').get().val()

    try:
        index2 = database2.child('Messages').child('index').get().val()
        messageList2 = database2.child('Messages').child('messageList').get().val()
        lastModified2 = database2.child('LastModified').get().val()
    except:
        index2 = database1.child('Messages').child('index').get().val()
        messageList2 = database1.child('Messages').child('messageList').get().val()
        lastModified2 = database2.child('LastModified').get().val()

    if lastModified1 == None:
        return index2, messageList2
    if lastModified2 == None:
        return index1, messageList1
    
    if lastModified1 >= lastModified2:
        return index1, messageList1
    else:
        return index2, messageList2


def addNewMessage(message):
    index, messageList = getAllMessages()

    if index == None:
        index = -1
    if messageList == None:
        messageList = []

    index = (index + 1) % 100
    if index >= len(messageList):
        messageList.append(message)
    else:
        messageList[index] = message

    try:
        database1.child('Messages').update({'index': index})
        database1.child('Messages').update({'messageList': messageList})
        database2.child('Messages').update({'index': index})
        database2.child('Messages').update({'messageList': messageList})
    except:
        try:
            database2.child('Messages').update({'index': index})
            database2.child('Messages').update({'messageList': messageList})
        except:
            pass


def synchronizeDBs():
    try:
        players1 = database1.child('Players').get().val()
        messages1 = database1.child('Messages').get().val()
        lastModified1 = database1.child('LastModified').get().val()
    except:
        return
    try:
        players2 = database2.child('Players').get().val()
        messages2 = database2.child('Messages').get().val()
        lastModified2 = database2.child('LastModified').get().val()
    except:
        return
    
    if lastModified1 == None and lastModified2 == None:
        return
    if lastModified1 == None:
        lastModified1 = 0
    if lastModified2 == None:
        lastModified2 = 0

    if lastModified1 >= lastModified2:
        if players1 == None:
            return
        database2.update({'Players': players1})
        if messages1 != None:
            database2.update({'Messages': messages1})
        database2.update({'LastModified': lastModified1})
    else:
        if players2 == None:
            return
        database1.update({'Players': players2})
        if messages2 != None:
            database1.update({'Messages': messages2})
        database1.update({'LastModified': lastModified2})


class Player():
    def __init__(self, name):
        self.name = name
        self.enemyLocation = [0,3000]
        self.bg_y = [0,-600]

        playerData = self.getPlayerData()
        if playerData != None:
            self.location = playerData['location']
            self.score = playerData['score']
            self.crash = playerData['crash']
            self.highscore = playerData['highscore']
            self.enemySpeed = playerData['enemySpeed']
        else:
            self.location = [0,0]
            self.score = 0
            self.crash = False
            self.highscore = 0
            self.enemySpeed = 0
            self.updateData()

    def getPlayerData(self):
        try:
            player1 = database1.child('Players').child(self.name).get().val()
            lastModified1 = database1.child('LastModified').get().val()
        except:
            player1 = database2.child('Players').child(self.name).get().val()
            lastModified1 = database2.child('LastModified').get().val()
        try:
            player2 = database2.child('Players').child(self.name).get().val()
            lastModified2 = database2.child('LastModified').get().val()
        except:
            player2 = database1.child('Players').child(self.name).get().val()
            lastModified2 = database1.child('LastModified').get().val()

        if lastModified1 == None:
            lastModified1 = 0
        if lastModified2 == None:
            lastModified2 = 0

        if lastModified1 >= lastModified2:
            if player1 == None:
                return None
            return dict(player1)
        else:
            if player2 == None:
                return None
            return dict(player2)

    def updateData(self):
        try:
            database1.child('Players').child(self.name).update({
                'location': self.location,
                'score': self.score,
                'crash': self.crash,
                'highscore': self.highscore,
                'enemySpeed': self.enemySpeed
            })
            database1.update({'LastModified': time.time()})
            database2.child('Players').child(self.name).update({
                'location': self.location,
                'score': self.score,
                'crash': self.crash,
                'highscore': self.highscore,
                'enemySpeed': self.enemySpeed
            })
            database2.update({'LastModified': time.time()})
        except:
            try:
                database2.child('Players').child(self.name).update({
                    'location': self.location,
                    'score': self.score,
                    'crash': self.crash,
                    'highscore': self.highscore,
                    'enemySpeed': self.enemySpeed
                })
                database2.update({'LastModified': time.time()})
            except:
                pass

    # def deletePlayer(self):
    #     try:
    #         database1.child('Players').child(self.name).remove()
    #         database2.child('Players').child(self.name).remove()
    #     except:
    #         try:
    #             database2.child('Players').child(self.name).remove()
    #         except:
    #             pass