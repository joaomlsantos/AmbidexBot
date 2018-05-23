from OpponentState import OpponentState

class PrivateState:

    def __init__(self,cValueBase):
        self.opponentStateArray = [OpponentState(),OpponentState(),OpponentState(),OpponentState(),OpponentState(),OpponentState(),OpponentState(),OpponentState()]
        self.promiseHistory = []
        self.decisionThreshold = 0
        self.emotionalMultiplier = 0

    
        