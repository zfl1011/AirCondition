from django.db import models

# Create your models here.

MODE = (
    ('1', 'Cooler'),
    ('2', 'Warmer'),
)

class Hotel(models.Model):
    startTime = models.FloatField(default=0.0)
    endTime = models.FloatField(default=0.0)#为0提示已经有一个在运行，要开启新的，先关闭旧的
    roomNum = models.IntegerField(default=5)
    serveUnitNum = models.IntegerField(default=6)
    Mode = models.IntegerField(default=1)
    # Mode = models.CharField(max_length=50, choices=MODE, default=MODE[1])
    tempLimitHigh = models.IntegerField(default=28)
    tempLimitLow = models.IntegerField(default=18)
    defaultTargetTemp = models.IntegerField(default=25)
    # feeRateH = models.FloatField(default=2.0)
    # feeRateM = models.FloatField(default=1.5)
    # 不同于静态结构设计，因为最终测试用例没有区分
    feeRateL = models.FloatField(default=1.0)
    isSchedulerRunning = models.IntegerField(default=0)
    oneServeTime = models.IntegerField(default=15)

    class Meta:
        db_table = "Hotel"

    # @staticmethod
    # def get_active():
    #     return Hotel.objects.filter(Mode = 1)

class WaitQueue(models.Model):
    order = models.IntegerField(default=-1) #-1是无需服务的 0是正在被服务 剩下的从120倒数
    roomID = models.IntegerField()

    class Meta:
        db_table = "WaitQueue"

STATE= (
    ('0', 'rest'),
    ('1', 'busy'),
    ('2', 'stop'),
)
class ServerUnit(models.Model):
    name = models.IntegerField()
    state = models.IntegerField(default=2)#('0', 'rest'),('1', 'busy'),('2', 'stop')
    # state = models.CharField(max_length=50, choices=STATE, default=STATE[2])

    class Meta:
        db_table = "ServerUnit"

class SchedulerLog(models.Model):
    serverID = models.IntegerField()
    roomID = models.IntegerField()
    requestID = models.IntegerField()
    startTime = models.FloatField(default=0.0)
    endTime = models.FloatField(default=0.0)
    fee = models.FloatField(default=0.0)

    class Meta:
        db_table = "SchedulerLog"