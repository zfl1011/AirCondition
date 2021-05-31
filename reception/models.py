from django.db import models
from inspector.models import SchedulerLog,Hotel
from user.models import RoomRequest,SPEED
from openpyxl import Workbook
# Create your models here.
class RDRManager(models.Manager):
    def creatRDR(self, time, roomID, timeIn, timeOut):
         list_RDR = []
         # 获取费率
         hotel = Hotel.objects.last()
         feeRates = hotel.feeRateL
         # 在数据库查找详单相关信息
         logs = SchedulerLog.objects.filter(roomID=roomID, startTime__range=[timeIn, timeOut])
         lastServeEnd = 0
         for record in logs:
             fee = record.fee
             requests = RoomRequest.objects.filter(roomID=roomID,speed__gt=-1, time__range=[lastServeEnd, record.endTime]).order_by("-pk")

             string_requests = ""
             requestDuration = round(record.endTime - record.startTime, 2)
             startTime = time.strftime("%Y.%m.%d-%H:%M:%S", time.localtime(record.startTime))
             if len(requests) == 0 :
                 print("one!!!!")
                 req = RoomRequest.objects.filter(roomID=roomID,time__lt=record.startTime).last()
                 requestTime = req.time
                 requestTime = time.strftime("%Y.%m.%d-%H:%M:%S", time.localtime(requestTime))
                 target_temp = req.targetTemp
                 fanSpeed = SPEED[req.speed + 1][1]
                 feeRate = feeRates
                 string_requests = requestTime + "_" + str(target_temp) + "℃_" + str(fanSpeed)
             else:
                for req in requests:
                    requestTime = req.time
                    requestTime = time.strftime("%Y.%m.%d-%H:%M:%S", time.localtime(requestTime))
                    target_temp = req.targetTemp
                    fanSpeed = SPEED[req.speed + 1][1]
                    feeRate = feeRates
                    if string_requests != "":
                        string_requests = string_requests + "__"
                    string_requests += requestTime+"-"+str(target_temp)+"℃-" + str(fanSpeed)
             list_RDR.append({"RoomId": roomID, "StartTime": startTime,
                          "ServerDuration": requestDuration, "FeeRate": feeRate,
                          "Fee": fee,"Requests":string_requests})
             lastServeEnd = record.endTime
         list_RDR.sort(key=lambda i: i["StartTime"])  # 按请求时间排序

         print(list_RDR)
         workbook = Workbook()
         sheet = workbook.create_sheet("详单", index=0)
         # 写入表头
         head = ["RoomId", "StartTime", "ServerDuration(s)", "FeeRate", "Fee", "Requests"]
         sheet.append(head)
         for item in list_RDR:
             sheet.append(
                 [item["RoomId"], item["StartTime"], item["ServerDuration"], item["FeeRate"], item["Fee"],
                  item["Requests"]])
         path = RDR.object.filter(roomID=roomID).last().position
         workbook.save(path)
         print("yes")
         return list_RDR

class RDR(models.Model):
    time = models.FloatField(default=0.0)
    roomID = models.IntegerField(default=0)
    timeIn = models.FloatField(default=0.0)
    timeOut = models.FloatField(default=0.0)
    position = models.CharField(max_length=100)#文件存储，都有单独的文件夹
    isPrint = models.IntegerField(default=0)
    object = RDRManager()
    class Meta:
        db_table = "RDR"

class Invoice(models.Model):
    time = models.FloatField(default=0.0)
    roomID = models.IntegerField(default=0)
    timeIn = models.FloatField(default=0.0)
    timeOut = models.FloatField(default=0.0)
    fee = models.FloatField(default=0.0)
    isPrint = models.IntegerField(default=0)
    class Meta:
        db_table = "Invoice"