from django.db import models

# Create your models here.
class Room(models.Model):
    roomID = models.IntegerField()
    time = models.FloatField(default=0.0)#好像没用？？只给request了//state的计一次服务时长
    temp = models.FloatField(default=0.0)#在request里没用，用于记录是否第一次请求，用来优先级
    fee = models.FloatField(default=0.0)

    class Meta:
        abstract = True #没有实际的表

STATE = (
    ('0','noRequest'),
    ('1','waitForServe'),#可能是需要被放到tmpC，也可能是waitforServe
    ('2','beServing'),
    ('3', 'tmpComplete'),
)

class RoomState(Room):
    state = models.IntegerField(default=0)
    plus = models.IntegerField(default=-1) #如果是13状态，就是requestID，2则是serverID，0则是-1

    class Meta:
        db_table = "RoomState"

SPEED = (
    ('-1','Stop'),
    ('0','High'),
    ('1','Middle'),
    ('2','Low'),
)
class RoomRequest(Room):
    speed = models.IntegerField(default=1)
    targetTemp = models.FloatField(default=26)

    class Meta:
        db_table = "RoomRequest"