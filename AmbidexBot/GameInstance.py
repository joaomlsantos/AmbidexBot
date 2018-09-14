import os

from Player import Player
from Color import Color
import random
from Type import Type
from Species import Species
from Status import Status
from Vote import Vote
from tabulate import tabulate
from operator import itemgetter

class GameInstance:
    
    def __init__(self,server):
        self.server = server
        self.PlayerArray = []
        self.InProgress = False
        self.GameStarted = False
        self.ActivePolling = False
        self.LockAmbidex = False
        self.AmbidexInProgress = False
        self.ColorSets = {}
        self.InitializeColorSets()
        self.GameIterations = 0
        self.CurrentColorSet = []
        self.CurrentDoorSet = []
        self.UserObjects = {}
        self.ProposedColorCombo = ""
        self.CurrentVotes = {}
        self.CurrentVotes["a"] = []
        self.CurrentVotes["b"] = []
        self.CurrentVotes["c"] = []
        self.AmbidexGameRound = {}
        self.MachinePersonalities = ["Cooperator","Undecided","Killer","Cockblocker","Asshole","Paranoid"]
        #self.MachineNames = ["Kye Dec","Sad Otter","Mac DeMarco","Pouty Maki","Mandy","Reinhardt","Kim Jong-Un","Sky The Magician","Brownie Cheesecake","Peter P. Porter","Funyarinpa","Hector Dec","Rick Green","Cass","Niklas Balk","Josharu Haegime","Daisy Peteller","Random Jamie Variant","Billie J. Gervaise","Masashiro Amane","Harry Peteller","Felix Dec","Samuel Dec","Eric Porter","Heinrich Porter","9th Man"]
        self.MachineNames = self.parseBotNamesFile("sadOttersNameList.txt")
        self.cyanLot = []
        self.yellowLot = []
        self.magentaLot = []
        self.redLot = []
        self.greenLot = []
        self.blueLot = []
        self.ColorLotMapping = {Color.CYAN: self.cyanLot, Color.YELLOW: self.yellowLot, Color.MAGENTA: self.magentaLot, Color.RED: self.redLot, Color.GREEN: self.greenLot, Color.BLUE: self.blueLot}
        self.lookupCombi = {"RED SOLO": (0,1,2), "RED PAIR": (0,2,1), "GREEN SOLO": (1,2,0), "GREEN PAIR":(1,0,2), "BLUE SOLO": (2,0,1), "BLUE PAIR": (2,1,0),"CYAN SOLO": (0,1,2), "CYAN PAIR": (0,2,1), "MAGENTA SOLO": (1,2,0), "MAGENTA PAIR":(1,0,2), "YELLOW SOLO": (2,0,1), "YELLOW PAIR": (2,1,0)}
        self.combinations = {"a": [[],[],[]], "b": [[],[],[]], "c": [[],[],[]]}
        self.playerObjectives = {}

        
    def clearGame(self):
        self.PlayerArray.clear()
        self.InProgress = False
        self.GameStarted = False
        self.ActivePolling = False
        self.LockAmbidex = False
        self.AmbidexInProgress = False
        self.GameIterations = 0
        self.CurrentColorSet.clear()
        self.CurrentDoorSet.clear()
        self.UserObjects.clear()
        self.ProposedColorCombo = ""
        self.CurrentVotes.clear()
        self.AmbidexGameRound.clear()
        self.CurrentVotes["y"] = 0
        self.CurrentVotes["n"] = 0
        self.ColorSets = {}
        self.InitializeColorSets()
        self.MachineNames = self.parseBotNamesFile("sadOttersNameList.txt")
        self.combinations = {"a": [[],[],[]], "b": [[],[],[]], "c": [[],[],[]]}
        self.playerObjectives = {}
        

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
            print(creatorName, "created a new game.")
            return True
        else:
            print(creatorName, "failed to create a game instance.")
            return False

    def endGame(self):
        self.clearGame()

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
        machinePlayer.setPersonality(random.choice(self.MachinePersonalities))
        self.PlayerArray.append(machinePlayer)
        print("Bot", machineName, "joined the current game.")
        print(machineName + "'s personality is " + machinePlayer.getPersonality())
        return machinePlayer


    def printPlayers(self):
        messageArray = []
        for player in self.PlayerArray:
            messageArray.append([player.getName(),player.getColor().name,player.getType().name])
            messageArray = sorted(messageArray,key=itemgetter(1,2))
        return tabulate(messageArray, headers=['Name', 'Color','Type'])

    def startGame(self):
        if(not self.checkPlayerLimit()):
            self.GameStarted = True
            self.GameIterations += 1
            self.randomizeBracelets()
            self.generatePlayerObjectives()
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






    def getOpponent(self,player):
        colortype = self.getPlayerColorType(player)     #aka "RED SOLO" or etc
        playerdoor = player.getDoor()                   #aka Color.CYAN
        for key in self.ColorSets[self.ProposedColorCombo].keys():
            if(key != colortype and self.ColorSets[self.ProposedColorCombo][key] == playerdoor):
                return key

    def getTempCombinations(self):
        message = ""
        self.cyanLot.clear()
        self.yellowLot.clear()
        self.magentaLot.clear()
        self.redLot.clear()
        self.greenLot.clear()
        self.blueLot.clear()
        for player in self.PlayerArray:
            bracelet = player.getColor().name + " " + player.getType().name
            playerDoor = self.ColorSets[self.ProposedColorCombo][bracelet]
            if(playerDoor == Color.CYAN):
                self.cyanLot.append(player)
            if(playerDoor == Color.YELLOW):
                self.yellowLot.append(player)
            if(playerDoor == Color.MAGENTA):
                self.magentaLot.append(player)
            if(playerDoor == Color.RED):
                self.redLot.append(player)
            if(playerDoor == Color.GREEN):
                self.greenLot.append(player)
            if(playerDoor == Color.BLUE):
                self.blueLot.append(player)
        if(len(self.cyanLot) != 0):
            message += self.cyanLot[0].getName() + ", " + self.cyanLot[1].getName() + " and " + self.cyanLot[2].getName() + " will go through the Cyan Door.\n"
            message += self.yellowLot[0].getName() + ", " + self.yellowLot[1].getName() + " and " + self.yellowLot[2].getName() + " will go through the Yellow Door.\n"
            message += self.magentaLot[0].getName() + ", " + self.magentaLot[1].getName() + " and " + self.magentaLot[2].getName() + " will go through the Magenta Door.\n"
        if(len(self.redLot) != 0):
            message += self.redLot[0].getName() + ", " + self.redLot[1].getName() + " and " + self.redLot[2].getName() + " will go through the Red Door.\n"
            message += self.greenLot[0].getName() + ", " + self.greenLot[1].getName() + " and " + self.greenLot[2].getName() + " will go through the Green Door.\n"
            message += self.blueLot[0].getName() + ", " + self.blueLot[1].getName() + " and " + self.blueLot[2].getName() + " will go through the Blue Door.\n"
        return message

    def generateRoundVote(self,player):
        personality = player.getPersonality()

        if(personality == "Cooperator"):
            return Vote.ALLY

        elif(personality == "Undecided"):
            if(random.random() > 0.5):
                return Vote.ALLY
            else:
                return Vote.BETRAY

        elif(personality == "Killer"):
            opponentColor = self.getOpponent(player).split()[0]
            opponentType = self.getOpponent(player).split()[1]
            for opponent in self.PlayerArray:
                if(opponent.getColor() == opponentColor and opponent.getType() == opponentType):
                    if (opponent.getPoints() <= 2):
                        return Vote.BETRAY
            return Vote.ALLY

        elif(personality == "Cockblocker"):
            opponentColor = self.getOpponent(player).split()[0]
            opponentType = self.getOpponent(player).split()[1]
            for opponent in self.PlayerArray:
                if(opponent.getColor() == opponentColor and opponent.getType() == opponentType):
                    if (opponent.getPoints() >= 6):
                        if(random.random() < 0.7):
                            return Vote.BETRAY
            return Vote.ALLY

        elif(personality == "Asshole"):
            return Vote.BETRAY

        elif(personality == "Paranoid"):
            if(self.GameIterations == 1 or player.getPoints() <= 2):
                return Vote.BETRAY
            else:
                 if(random.random() > 0.6):
                     return Vote.ALLY
                 else:
                     return Vote.BETRAY



    def getAmbidexResult(self,playerColorType,opponentColorType):
        playerVote = self.AmbidexGameRound[playerColorType]
        opponentVote = self.AmbidexGameRound[opponentColorType]
        if(playerVote == Vote.ALLY and opponentVote == Vote.ALLY):
            return 2
        elif(playerVote == Vote.ALLY and opponentVote == Vote.BETRAY):
            return -2
        elif(playerVote == Vote.BETRAY and opponentVote == Vote.ALLY):
            return 3
        elif(playerVote == Vote.BETRAY and opponentVote == Vote.BETRAY):
            return 0
        


    def setPlayerDoors(self,combi):
        self.clearDoorLots()
        self.setProposedColorCombo(combi)
        for player in self.PlayerArray:
            bracelet = player.getColor().name + " " + player.getType().name
            playerCombi = self.lookupCombi[bracelet]
            if(combi == "a"):
                playerCombi = playerCombi[0]
            elif(combi == "b"):
                playerCombi = playerCombi[1]
            elif(combi == "c"):
                playerCombi = playerCombi[2]
            player.setDoor(self.getDoorFromCombi(playerCombi,player))


    def initPollingDict(self):
        self.CurrentVotes.clear()
        self.CurrentVotes["a"] = []
        self.CurrentVotes["b"] = []
        self.CurrentVotes["c"] = []

    def voteTally(self):
        message = ""
        for key in self.CurrentVotes.keys():
            message += key.upper() + "(" + str(len(self.CurrentVotes[key])) + ") - "
            for player in self.CurrentVotes[key]:
                message += player.name + ", "
            message += "\n"
        return message;


    def erasePlayerVote(self,player):
        for key in self.CurrentVotes.keys():
            if player in self.CurrentVotes[key]:
                self.CurrentVotes[key].remove(player);


    def getAlivePlayers(self):      #it only counts HUMAN players right now
        result = 0
        for player in self.PlayerArray:
            if(player.getStatus() == Status.ALIVE and player.getSpecies() == Species.HUMAN):
                result += 1
        return result


    def clearDoorLots(self):
        self.cyanLot.clear()
        self.yellowLot.clear()
        self.magentaLot.clear()
        self.redLot.clear()
        self.greenLot.clear()
        self.blueLot.clear()

    def checkInProgress(self):
        return (self.InProgress)

    def checkGameStarted(self):
        return (self.GameStarted)

    def checkPlayer(self,playerName):
        for p in self.PlayerArray:
            if(p.getName() == playerName):
                return True
        return False

    def getPlayer(self,playerName):
        for p in self.PlayerArray:
            if(p.getName() == playerName):
                return p

    def getPlayerColorType(self,player):
        return player.getColor().name + " " + player.getType().name


    def checkPlayerLimit(self):
        return(len(self.PlayerArray) < 9)


    def getPlayerByTypecolor(self,typecolorString):
        resultArray = []

        for player in self.PlayerArray:
            if(self.getPlayerColorType(player) == typecolorString):
                resultArray.append(player)

        return resultArray


    def parseBotNamesFile(self,filename):
        file = open(os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))), filename),'r')
        names = file.read().splitlines()
        file.close()
        return names




    def generateSingleObjective(self):

        intKill = 15            #between 0 and 14
        intTrapInside = 70           #between 15 and 69
        intEscapeWith = 100     #between 70 and 99
        randomNumber = random.randrange(100)

        if(randomNumber < intKill):
            return "KILL"

        elif(randomNumber >= intKill and randomNumber < intTrapInside):
            return "TRAP_INSIDE"

        elif(randomNumber >= intTrapInside and randomNumber < intEscapeWith):
            return "ESCAPE_WITH"


    def generateObjectiveTarget(self,player):
        
        targets = list(self.PlayerArray)
        targets.remove(player)
        
        randomNumber = random.randrange(len(targets))

        return targets[randomNumber].getName()


    def generatePlayerObjectives(self):
        for player in self.PlayerArray:
            selectObjective = self.generateSingleObjective()
            selectTarget = self.generateObjectiveTarget(player)
            self.playerObjectives[player.getName()] = (selectObjective, selectTarget)


    def checkObjectiveMet(self,playerName):
        objective = self.playerObjectives[playerName][0]
        targetName = self.playerObjectives[playerName][1]       #target name, not target object
        player = self.getPlayer(playerName)
        target = self.getPlayer(targetName)
        if(player.status == Status.ALIVE):
            if((objective == "KILL" and target.status == Status.DEAD) or (objective == "TRAP_INSIDE" and target.points < 9) or (objective == "ESCAPE_WITH" and target.points >= 9 and target.status == Status.ALIVE)):
                return True
            else:
                return False
        else:
            return False
    

    def getObjectiveMsg(self,playerName):
        objective = self.playerObjectives[playerName][0]
        targetName = self.playerObjectives[playerName][1]       #target name, not target object
        message = "Objective: Escape and "
        if(objective == "KILL"):
            message += "KILL " + targetName + ".```\n"
        elif(objective == "TRAP_INSIDE"):
            message += "TRAP " + targetName + " INSIDE the facility.```\n"
        elif(objective == "ESCAPE_WITH"):
            message += "MAKE SURE " + targetName + " ESCAPES the facility.```\n"
        return message


    def setPlayerCombi(self,player):
        
        colorType = self.getPlayerColorType(player)
        playerCombi = self.lookupCombi[colorType]
        playerLots = [list(self.combinations["a"]),list(self.combinations["b"]),list(self.combinations["c"])]
        playerLots[0][playerCombi[0]].append(player)
        playerLots[1][playerCombi[1]].append(player)
        playerLots[2][playerCombi[2]].append(player)
        self.combinations["a"] = playerLots[0]
        self.combinations["b"] = playerLots[1]
        self.combinations["c"] = playerLots[2]


    def getDoorFromCombi(self,combiNumber,player):
        if(self.GameIterations%2 != 0):
            if(combiNumber == 0):
                self.cyanLot.append(player)
                return Color.CYAN
            elif(combiNumber == 1):
                self.magentaLot.append(player)
                return Color.MAGENTA
            elif(combiNumber == 2):
                self.yellowLot.append(player)
                return Color.YELLOW
        else:
            if(combiNumber == 0):
                self.redLot.append(player)
                return Color.RED
            elif(combiNumber == 1):
                self.greenLot.append(player)
                return Color.GREEN
            elif(combiNumber == 2):
                self.blueLot.append(player)
                return Color.BLUE




    def setProposedColorCombo(self,combiNumber):
        if(self.GameIterations%2 != 0):
            if(combiNumber == "a"):
                self.ProposedColorCombo = "RedSolo|RedPair"
            elif(combiNumber == "b"):
                self.ProposedColorCombo = "RedSolo|BluePair"
            elif(combiNumber == "c"):
                self.ProposedColorCombo = "RedSolo|GreenPair"
        else:
            if(combiNumber == "a"):
                self.ProposedColorCombo = "CyanSolo|CyanPair"
            elif(combiNumber == "b"):
                self.ProposedColorCombo = "CyanSolo|YellowPair"
            elif(combiNumber == "c"):
                self.ProposedColorCombo = "CyanSolo|MagentaPair"

    def clearCombi(self):
        self.combinations = {"a": [[],[],[]], "b": [[],[],[]], "c": [[],[],[]]}