from Player import Player
from Color import Color
import random
from Type import Type
from Species import Species

class GameInstance:
    
    def __init__(self):
        self.PlayerArray = []
        self.InProgress = False
        self.GameStarted = False
        self.ColorSets = {}
        self.ColorSets["Primary Colors"] = [Color.RED,Color.GREEN,Color.BLUE]
        self.ColorSets["Complementary Colors"] = [Color.CYAN,Color.YELLOW,Color.MAGENTA]
        self.GameIterations = 0
        self.CurrentColorSet = []
        self.CurrentDoorSet = []
        self.UserObjects = {}
        self.MachineNames = ["Kye Dec","Sad Otter","Mac DeMarco","Pouty Maki","Mandy","Reinhardt","Kim Jong-Un","Sky The Magician","Brownie Cheesecake"]

    def createGame(self,creatorName,creatorObject):
        if(not self.InProgress):
            self.PlayerArray.append(Player(creatorName,Species.HUMAN))
            self.UserObjects[creatorName] = creatorObject
            self.InProgress = True
            print("Player Array: ", self.PlayerArray)
            print(creatorName, "created a new game.")
            return True
        else:
            print(creatorName, "failed to create a game instance.")
            return False

    def endGame(self,ender):
        self.clearGame()
        print(ender, "ended the game.")

    def joinGame(self,playerName,playerObject):
        if(not self.checkPlayer(playerName)):
            self.PlayerArray.append(Player(playerName,Species.HUMAN))
            self.UserObjects[playerName] = playerObject
            print(playerName, "joined the current game.")
            return True
        else:
            print("Error:", playerName, "is already in the game.")
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

    def addMachine(self):
        machineName = random.choice(self.MachineNames)
        self.MachineNames.remove(machineName)
        machinePlayer = Player(machineName,Species.MACHINE)
        self.PlayerArray.append(machinePlayer)
        print("Bot ", machineName, "joined the current game.")
        return machinePlayer

    def checkInProgress(self):
        return (self.InProgress)

    def checkGameStarted(self):
        return (self.GameStarted)

    def checkPlayer(self,player):
        for p in self.PlayerArray:
            if(p.getName() == player):
                return True
        return False

    def getPlayer(self,player):
        for p in self.PlayerArray:
            if(p.getName() == player):
                return p

    def clearGame(self):
        self.PlayerArray.clear()
        self.InProgress = False
        self.GameIterations = 0
        self.CurrentColorSet = []
        self.CurrentDoorSet = []
        self.UserObjects = {}
        self.MachineNames = ["Kye Dec","Sad Otter","Mac DeMarco","Pouty Maki","Mandy","Reinhardt","Kim Jong-Un","Sky The Magician","Brownie Cheesecake"]


    def checkPlayerLimit(self):
        return(len(self.PlayerArray) < 9)

    def printPlayers(self):
        message = ""
        for player in self.PlayerArray:
            message += player.name + ", "
        return message[:-2]

    def startGame(self):
        if(not self.checkPlayerLimit()):
            self.GameStarted = True
            self.GameIterations += 1
            self.randomizeBracelets()
            return True
        else:
            return False
            
    def randomizeBracelets(self):
        playerSet = self.PlayerArray.copy()
        finalSet = []
        if(self.GameIterations%2 != 0):
            self.CurrentColorSet = self.ColorSets["Primary Colors"]
            self.CurrentDoorSet = self.ColorSets["Complementary Colors"]
        elif(self.GameIterations%2 == 0):
            self.CurrentColorSet = self.ColorSets["Complementary Colors"]
            self.CurrentDoorSet = self.ColorSets["Primary Colors"]
        for color in self.CurrentColorSet:
            player = playerSet[random.randint(0,len(playerSet)-1)]
            playerSet.remove(player)
            player.setColor(color)
            player.setType(Type.SOLO)
            finalSet.append(player)
            for i in range(0,2):
                player = playerSet[random.randint(0,len(playerSet)-1)]
                playerSet.remove(player)
                player.setColor(color)
                player.setType(Type.PAIR)
                finalSet.append(player)
        self.PlayerArray = finalSet

