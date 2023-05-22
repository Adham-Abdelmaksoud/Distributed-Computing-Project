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


# def getAllPlayersData():
#     players = database1.child('Players').get()
#     return dict(players.val())

# def getPlayersCount():
#     return len(database1.child('Players').get().val())

# def deleteAllPLayers():
#     database1.child('Players').remove()


class Player():
    def __init__(self, id, name, location):
        self.id = id
        self.name = name
        self.location = location
        try:
            database1.child('Players').child(self.id).set({
                'name': self.name,
                'location': self.location
            })
            database2.child('Players').child(self.id).set({
                'name': self.name,
                'location': self.location
            })
        except:
            try:
                database2.child('Players').child(self.id).set({
                    'name': self.name,
                    'location': self.location
                })
            except:
                pass

    def getPlayerData(self):
        try:
            player = database1.child('Players').child(self.id).get()
        except:
            player = database2.child('Players').child(self.id).get()
        return dict(player.val())
    
    def deletePlayer(self):
        try:
            database1.child('Players').child(self.id).remove()
            database2.child('Players').child(self.id).remove()
        except:
            try:
                database2.child('Players').child(self.id).remove()
            except:
                pass

    def updateLocation(self):
        try:
            database1.child('Players').child(self.id).update({
                'location': self.location,
            })
            database2.child('Players').child(self.id).update({
                'location': self.location,
            })
        except:
            try:
                database2.child('Players').child(self.id).update({
                    'location': self.location,
                })
            except:
                pass