from Status import Status
from Color import Color
from Type import Type
from Species import Species

class Player:

    def __init__(self, name,species):
        self.name = name
        self.status = Status.ALIVE
        self.points = 3
        self.color = Color.BLACK
        self.type = Type.UNDEFINED
        self.species = species
        self.door = Color.BLACK

    def addPoints(self, amount):
        self.points += amount

    def subPoints(self, amount):
        self.points -= amount
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