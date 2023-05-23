
import pyrebase

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


def getAllPlayersData():
    try:
        players = database1.child('Players').get()
    except:
        players = database2.child('Players').get()
    return dict(players.val())

def isDBEmpty():
    try:
        players = database1.child('Players').shallow().get().val()
    except:
        players = database2.child('Players').shallow().get().val()
    if players == None:
        return True
    return False

def deleteAllPLayers():
    try:
        database1.child('Players').remove()
        database2.child('Players').remove()
    except:
        try:
            database2.child('Players').remove()
        except:
            pass

def isPlayerInDB(name):
    if isDBEmpty():
        return False
    players = getAllPlayersData()
    if name in players.keys():
        return True
    return False


class Player():
    def __init__(self, name, location,score):
        if isPlayerInDB(name):
            self.name = name
            playerData = self.getPlayerData()
            self.location = playerData['location']
            self.score = playerData['score']
        
        else:
            self.name = name
            self.location = location
            self.score = score
            try:
                database1.child('Players').child(self.name).set({
                    'name': self.name,
                    'location': self.location,
                    'score':self.score
                })
                database2.child('Players').child(self.name).set({
                    'name': self.name,
                    'location': self.location,
                    'score':self.score
                })
            except:
                try:
                    database2.child('Players').child(self.name).set({
                        'name': self.name,
                        'location': self.location,
                        'score':self.score
                    })
                except:
                    pass

    def getPlayerData(self):
        try:
            player = database1.child('Players').child(self.name).get()
        except:
            player = database2.child('Players').child(self.name).get()
        return dict(player.val())

    def deletePlayer(self):
        try:
            database1.child('Players').child(self.name).remove()
            database2.child('Players').child(self.name).remove()
        except:
            try:
                database2.child('Players').child(self.name).remove()
            except:
                pass

    def updateLocation(self):
        try:
            database1.child('Players').child(self.name).update({
                'location': self.location,
            })
            database2.child('Players').child(self.name).update({
                'location': self.location,
            })
        except:
            try:
                database2.child('Players').child(self.name).update({
                    'location': self.location,
                })
            except:
                pass

    def updateScore(self):
        try:
            database1.child('Players').child(self.name).update({
                'score': self.score,
            })
            database2.child('Players').child(self.name).update({
                'score': self.score,
            })
        except:
            try:
                database2.child('Players').child(self.name).update({
                    'score': self.score,
                })
            except:
                pass


