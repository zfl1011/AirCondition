class Room:
    count = 0
    def __init__(self):
        Room.count +=1
        self.isServe = 0
        self.temp = 26.30
        self.request = 0
        self.speed = -1 
        self.target = -1
        self.roomId = self.count
    def requestOn(self,temp,speed,target):
        self.temp = temp
        self.request = 1
        self.speed = speed
        self.target = target
    def requestOff(self,temp,speed,target):
        self.temp = temp
        self.request = 0
        self.speed = -1
        self.target = -1