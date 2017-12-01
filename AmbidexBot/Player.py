from Status import Status
from Color import Color
from Type import Type

class Player:

    def __init__(self, name):
        self.name = name
        self.status = Status.ALIVE
        self.points = 3
        self.color = Color.BLACK
        self.type = None

    def addPoints(self, amount):
        self.points += amount

    def subPoints(self, amount):
        self.points -= amount
        if(self.points <= 0):
            self.status = Status.DEAD

    def defineColor(self, color):
        self.color = color

    def defineType(self, type):
        self.type = type

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