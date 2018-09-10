from Status import Status
from Color import Color
from Type import Type
from Species import Species

class Player:

    def __init__(self,name,species):
        self.name = name
        self.status = Status.ALIVE
        self.points = 3
        self.color = Color.BLACK
        self.type = Type.UNDEFINED
        self.species = species
        self.door = Color.BLACK
        self.personality = ""

    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name

    def addPoints(self, amount):
        self.points += amount
        if(self.points <= 0):
            self.status = Status.DEAD

    def setColor(self, color):
        self.color = color

    def setType(self, type):
        self.type = type

    def setSpecies(self, species):
        self.species = species

    def setDoor(self, door):
        self.door = door

    def setPersonality(self, personality):
        self.personality = personality

    def getName(self):
        return self.name

    def getStatus(self):
        return self.status

    def getPoints(self):
        return self.points

    def getColor(self):
        return self.color

    def getType(self):
        return self.type

    def getSpecies(self):
        return self.species

    def getDoor(self):
        return self.door

    def getPersonality(self):
        return self.personality