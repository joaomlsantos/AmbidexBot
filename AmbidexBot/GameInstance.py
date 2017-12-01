from Player import Player

class GameInstance:
    
    def __init__(self):
        self.PlayerArray = []
        self.InProgress = False

    def createGame(self,creator):
        if(not self.InProgress):
            self.PlayerArray.append(Player(creator))
            self.InProgress = True
            print("Player Array: ", self.PlayerArray)
            print(creator, "created a new game.")
            return True
        else:
            print(creator, "failed to create a game instance.")
            return False

    def endGame(self,ender):
        self.clearGame()
        print(ender, "ended the game.")

    def joinGame(self,player):
        if(not self.checkPlayer(player)):
            self.PlayerArray.append(Player(player))
            print(player, "joined the current game.")
            return True
        else:
            print("Error:", player, "is already in the game.")
            return False

    def quitGame(self,player):
        for p in self.PlayerArray:
            if(p.getName() == player):
                self.PlayerArray.remove(p)
                if(len(self.PlayerArray) == 0):
                    self.clearGame()
                return True
        print("Error:", player, "tried to quit a game they were not in.")
        return False

    def checkInProgress(self):
        return (self.InProgress)

    def checkPlayer(self,player):
        for p in self.PlayerArray:
            if(p.getName() == player):
                return True
        return False

    def clearGame(self):
        self.PlayerArray.clear()
        self.InProgress = False

    def checkPlayerLimit(self):
        return(len(self.PlayerArray) < 9)