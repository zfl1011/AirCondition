import os

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from user.models import RoomRequest
from inspector.models import SchedulerLog
from reception.models import RDR
import time

from openpyxl import Workbook

# Create your models here.
class ReportManager(models.Manager):
    def creatReport(self, stime, roomList, type,nametype):
        print("in creat",type)
        if type == "0":
            print("type==0")
            range = 3600 * 24
        elif type == "1":
            range = 3600 * 24 * 7
        elif type == "2":
            range = 3600 * 24 * 30
        else:
            range = 3600 * 24 * 365
        # 开关次数，使用空调的时长，总费用，被调度的次数、详单数、调温次数、调风次数
        #{ {"id":2,"on":23,"dur":30.4,"fee":898,"beS":1222,"RDR":13,"fan":12,"temp":22},
        # {...},...
        # }
        list_report = []
        for r in roomList:
            print("room",r)
            #从roomrequest查 开关次数 调风 调温
            allrq = RoomRequest.objects.filter(roomID=r, time__range=[stime-range, stime])
            ontime = 0
            fan = 0
            temp = 0
            lasts = 1
            lastisoff = 0
            if len(allrq)>0 :
                if allrq[len(allrq)-1].speed != -1:
                    ontime += 1
                lastt = allrq[0].targetTemp
                for rq in allrq:
                    if rq.speed == -1:
                        ontime += 1
                        lastisoff = 1
                    else:
                        if lastisoff == 0 and rq.speed != lasts:
                            fan += 1
                            print("rpk=",rq.pk,"fan++")
                        if lastisoff == 0 and rq.targetTemp != lastt:
                            temp +=1
                            print("rpk=",rq.pk,"temp++")
                        lasts = rq.speed
                        lastt = rq.targetTemp
                        lastisoff = 0
            #从schedulog 时长 费用 调度次数
            logs = SchedulerLog.objects.filter(roomID=r, startTime__range=[stime-range, stime])
            dur = 0
            fee = 0
            beS = len(logs)
            for log in logs:
                dur += log.endTime-log.startTime
                fee += log.fee
            dur = round(dur,2)
            fee = round(fee,2)
            # 从RDR查
            RDRs = RDR.object.filter(roomID=r, time__range=[stime-range, stime])
            rdr = len(RDRs)
            #存list  {"id":2,"on":23,"dur":30.4,"fee":898,"beS":1222,"RDR":13,"fan":12,"temp":22},
            list_report.append({"id":r,"on":ontime,"dur":dur,"fee":fee,"beS":beS,"RDR":rdr,"fan":fan,"temp":temp})
            print(list_report[len(list_report)-1])
        #存文件
        workbook = Workbook()
        sheet = workbook.create_sheet("详单", index=0)
        # 写入表头 开关次数，使用空调的时长，总费用，被调度的次数、详单数、调温次数、调风次数
        head = ["房间号", "开关次数", "使用空调总时长", "总费用", "被调度的次数", "详单数","调风次数", "调温次数"]
        sheet.append(head)
        for item in list_report:
            sheet.append(
                [item["id"], item["on"], item["dur"], item["fee"], item["beS"],
                 item["RDR"],item["fan"],item["temp"]])
        path = "File_Report/" + time.strftime("%Y-%m-%d",time.localtime(time.time()))+"-"+str(len(Report.object.all())) +"-"+nametype+ ".xlsx"
        workbook.save(path)
        print("yes")
        return list_report
        #把相关信息存到数据库

        # print("{", "\"开关次数\":", onOffTimes,
        #       ",\"调度总时间\":", scheduleTotTime,
        #       ",\"总价格\":", totFee,
        #       ",\"调度次数\":", scheduleTimes,
        #       ",\"详单数\":", RDRTimes,
        #       ",\"调温次数\":", tempTimes,
        #       ",\"调风次数\":", speedTimes,
        #       "}", file=fp)




class Report(models.Model):
    time = models.FloatField(default=0.0)
    roomList = models.CharField(validators=[validate_comma_separated_integer_list], max_length=10, blank=True,
                                null=True, default='')
    type = models.IntegerField(default=1)  # 日周月年1234
    date = models.CharField(default=0,max_length=100)
    position = models.CharField(max_length=100)  # 文件存储，此处存放其路径&文件名
    object = ReportManager()
    class Meta:
        db_table = "Report"
