from Player import Player
from Color import Color
import random
from Type import Type
from Species import Species

class GameInstance:
    
    def __init__(self,server):
        self.server = server
        self.PlayerArray = []
        self.InProgress = False
        self.GameStarted = False
        self.ActivePolling = False
        self.ColorSets = {}
        self.InitializeColorSets()
        self.GameIterations = 0
        self.CurrentColorSet = []
        self.CurrentDoorSet = []
        self.UserObjects = {}
        self.ProposedColorCombo = {}
        self.CurrentVotes = {}
        self.CurrentVotes["y"] = 0
        self.CurrentVotes["n"] = 0
        self.MachineNames = ["Kye Dec","Sad Otter","Mac DeMarco","Pouty Maki","Mandy","Reinhardt","Kim Jong-Un","Sky The Magician","Brownie Cheesecake"]

    def InitializeColorSets(self):
        self.ColorSets["Primary Colors"] = [Color.RED,Color.GREEN,Color.BLUE]
        self.ColorSets["Complementary Colors"] = [Color.CYAN,Color.YELLOW,Color.MAGENTA]
        self.ColorSets["RedSolo|RedPair"] = {"RED SOLO": Color.CYAN, "RED PAIR": Color.CYAN, "GREEN SOLO": Color.MAGENTA, "GREEN PAIR": Color.MAGENTA, "BLUE SOLO": Color.YELLOW, "BLUE PAIR": Color.YELLOW }
        self.ColorSets["RedSolo|GreenPair"] = {"RED SOLO": Color.YELLOW, "RED PAIR": Color.MAGENTA, "GREEN SOLO": Color.CYAN, "GREEN PAIR": Color.YELLOW, "BLUE SOLO": Color.MAGENTA, "BLUE PAIR": Color.CYAN }
        self.ColorSets["RedSolo|BluePair"] = {"RED SOLO": Color.MAGENTA, "RED PAIR": Color.YELLOW, "GREEN SOLO": Color.YELLOW, "GREEN PAIR": Color.CYAN, "BLUE SOLO": Color.CYAN, "BLUE PAIR": Color.MAGENTA }
        self.ColorSets["CyanSolo|CyanPair"] = {"CYAN SOLO": Color.RED, "CYAN PAIR": Color.RED, "YELLOW SOLO": Color.BLUE, "YELLOW PAIR": Color.BLUE, "MAGENTA SOLO": Color.GREEN, "MAGENTA PAIR": Color.GREEN }
        self.ColorSets["CyanSolo|YellowPair"] = {"CYAN SOLO": Color.GREEN, "CYAN PAIR": Color.BLUE, "YELLOW SOLO": Color.RED, "YELLOW PAIR": Color.GREEN, "MAGENTA SOLO": Color.BLUE, "MAGENTA PAIR": Color.RED }
        self.ColorSets["CyanSolo|MagentaPair"] = {"CYAN SOLO": Color.BLUE, "CYAN PAIR": Color.GREEN, "YELLOW SOLO": Color.GREEN, "YELLOW PAIR": Color.RED, "MAGENTA SOLO": Color.RED, "MAGENTA PAIR": Color.BLUE }


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
        self.ProposedColorCombo = {}
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

    def calculateCombinations(self,soloPlayer,pairPlayer):
        if((soloPlayer.getColor() == Color.RED and pairPlayer.getColor() == Color.RED) or (soloPlayer.getColor() == Color.GREEN and pairPlayer.getColor() == Color.GREEN) or (soloPlayer.getColor() == Color.BLUE and pairPlayer.getColor() == Color.BLUE)):
            colorCombo = "RedSolo|RedPair"
        if((soloPlayer.getColor() == Color.RED and pairPlayer.getColor() == Color.GREEN) or (soloPlayer.getColor() == Color.GREEN and pairPlayer.getColor() == Color.BLUE) or (soloPlayer.getColor() == Color.BLUE and pairPlayer.getColor() == Color.RED)):
            colorCombo = "RedSolo|GreenPair"
        if((soloPlayer.getColor() == Color.RED and pairPlayer.getColor() == Color.BLUE) or (soloPlayer.getColor() == Color.GREEN and pairPlayer.getColor() == Color.RED) or (soloPlayer.getColor() == Color.BLUE and pairPlayer.getColor() == Color.GREEN)):
            colorCombo = "RedSolo|BluePair"
        if((soloPlayer.getColor() == Color.CYAN and pairPlayer.getColor() == Color.CYAN) or (soloPlayer.getColor() == Color.YELLOW and pairPlayer.getColor() == Color.YELLOW) or (soloPlayer.getColor() == Color.MAGENTA and pairPlayer.getColor() == Color.MAGENTA)):
            colorCombo = "CyanSolo|CyanPair"
        if((soloPlayer.getColor() == Color.CYAN and pairPlayer.getColor() == Color.YELLOW) or (soloPlayer.getColor() == Color.YELLOW and pairPlayer.getColor() == Color.MAGENTA) or (soloPlayer.getColor() == Color.MAGENTA and pairPlayer.getColor() == Color.CYAN)):
            colorCombo = "CyanSolo|YellowPair"
        if((soloPlayer.getColor() == Color.CYAN and pairPlayer.getColor() == Color.MAGENTA) or (soloPlayer.getColor() == Color.YELLOW and pairPlayer.getColor() == Color.CYAN) or (soloPlayer.getColor() == Color.MAGENTA and pairPlayer.getColor() == Color.YELLOW)):
            colorCombo = "CyanSolo|MagentaPair"
        self.ProposedColorCombo = colorCombo
        return self.getTempCombinations()

    def getTempCombinations(self):
        message = ""
        cyanLot = []
        yellowLot = []
        magentaLot = []
        redLot = []
        greenLot = []
        blueLot = []
        for player in self.PlayerArray:
            bracelet = player.getColor().name + " " + player.getType().name
            playerDoor = self.ColorSets[self.ProposedColorCombo][bracelet]
            if(playerDoor == Color.CYAN):
                cyanLot.append(player)
            if(playerDoor == Color.YELLOW):
                yellowLot.append(player)
            if(playerDoor == Color.MAGENTA):
                magentaLot.append(player)
            if(playerDoor == Color.RED):
                redLot.append(player)
            if(playerDoor == Color.GREEN):
                greenLot.append(player)
            if(playerDoor == Color.BLUE):
                blueLot.append(player)
        if(len(cyanLot) != 0):
            message += cyanLot[0].getName() + ", " + cyanLot[1].getName() + " and " + cyanLot[2].getName() + " will go through the Cyan Door.\n"
            message += yellowLot[0].getName() + ", " + yellowLot[1].getName() + " and " + yellowLot[2].getName() + " will go through the Yellow Door.\n"
            message += magentaLot[0].getName() + ", " + magentaLot[1].getName() + " and " + magentaLot[2].getName() + " will go through the Magenta Door.\n"
        if(len(redLot) != 0):
            message += redLot[0].getName() + ", " + redLot[1].getName() + " and " + redLot[2].getName() + " will go through the Red Door.\n"
            message += greenLot[0].getName() + ", " + greenLot[1].getName() + " and " + greenLot[2].getName() + " will go through the Green Door.\n"
            message += blueLot[0].getName() + ", " + blueLot[1].getName() + " and " + blueLot[2].getName() + " will go through the Blue Door.\n"
        return message

        

    def setPlayerDoors(self):
        for player in PlayerArray:
            bracelet = player.getColor().name + " " + player.getType().name
            player.setDoor(self.ColorSets[self.ProposedColorCombo][bracelet])
