import threading

from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from common import Room

# Create your views here.
from .models import Hotel, ServerUnit, WaitQueue,SchedulerLog
from user.models import RoomState, RoomRequest, SPEED
from .scheduler import Scheduler
from common import helper
import time
scheduler = None

def index(request):
    return render(request, 'inspector.html')


def powerOn(request):
    global scheduler
    # stateStr = ""
    # hotel = Hotel.objects.filter(endTime=0)
    # if len(hotel) == 0:
    #     hotel = Hotel.objects.create(startTime=time.time())
    #     hotel.save()
    #     stateStr = "normal "+time.asctime(time.localtime(hotel.startTime))
    # elif len(hotel) > 1:
    #     for h in hotel:
    #         print(h.startTime)
    #         h.endTime = time.time()
    #         h.save()
    #     hotel = Hotel.objects.create(startTime=time.time())
    #     hotel.save()
    #     stateStr = "multy, shut-down all, and create new: "+time.asctime(time.localtime(hotel.startTime))
    # else:
    #     stateStr = "already " + time.asctime(time.localtime(hotel[0].startTime))
    #     hotel = hotel[0]
    if helper.hotelOn():
        hotel = Hotel.objects.filter(endTime=0)
        hotel = hotel[0]
        stateStr = "already " #也需要初始化+ time.asctime(time.localtime(hotel[0].startTime))
    else:
        hotel = Hotel.objects.create(startTime=time.time())
        hotel.save()
        stateStr = "ON "+time.asctime(time.localtime(hotel.startTime))

    # 初始化服务对象ServerUnit
    i = 1
    while i <= hotel.serveUnitNum:
        unit = ServerUnit.objects.filter(name = i)
        if len(unit) == 0:
            unit = ServerUnit.objects.create(name = i)
        elif len(unit) > 1:
            for u in unit:
                print("delete")
                u.delete()
            unit = ServerUnit.objects.create(name=i)
        else:
            unit = unit[0]
        unit.state = 0
        unit.save()
        i += 1
    # 初始化房间RoomState
    i = 1
    while i <= hotel.roomNum :
        room = RoomState.objects.filter(roomID = i)
        if len(room) == 0:
            room = RoomState.objects.create(roomID = i)
        elif len(room) > 1:
            for r in room:
                print("delete")
                r.delete()
            room = RoomState.objects.create(roomID=i)
        else:
            room = room[0]
            room.state = 0
            room.fee = 0
            room.plus = -1
        room.save()
        i += 1
    # 初始化等待队列WaitQueue
    i = 1
    while i <= hotel.roomNum:
        room = WaitQueue.objects.filter(roomID=i)
        if len(room) == 0:
            room = WaitQueue.objects.create(roomID=i)
        elif len(room) > 1:
            for r in room:
                print("delete")
                r.delete()
            room = WaitQueue.objects.create(roomID=i)
        else:
            room = room[0]
            room.order = 0
        room.save()
        i += 1
    # 初始化scheduler 调度者
    scheduler = Scheduler(hotel.serveUnitNum, hotel.Mode)
    return HttpResponse(stateStr)

def setPara(request):
    # TODO
    global scheduler
    if scheduler == None:
        return HttpResponse("scheduler == None, startUp failed, please try powerOn")
    hotel = Hotel.objects.filter(endTime=0)
    if len(hotel) > 1:
        return HttpResponse("startUp failed, please try powerOn")
    hotel = hotel[0]
    hotel.Mode = request.GET.get('Mode')
    hotel.defaultTargetTemp = request.GET.get('DT')
    hotel.tempLimitHigh = request.GET.get('HT')
    hotel.tempLimitLow = request.GET.get('LT')
    hotel.feeRateL = request.GET.get('fee')
    # if int(hotel.Mode) == 1:
    #     hotel.defaultTargetTemp = 25
    #     hotel.tempLimitHigh = 28
    # else:
    #     hotel.defaultTargetTemp = 22
    #     hotel.tempLimitHigh = 25
    hotel.save()
    return HttpResponse("ok")

def startUp(request):
    global scheduler
    if scheduler == None:
        return HttpResponse("scheduler == None, startUp failed, please try powerOn")
    hotel = Hotel.objects.filter(endTime=0)
    if len(hotel) > 1:
        return HttpResponse("startUp failed, please try powerOn")
    scheduler.isReady = 1
    hotel = hotel[0]
    scheduler.mode = hotel.Mode
    hotel.isSchedulerRunning = 1
    hotel.save()
    # scheduler.runThreadKeepOrder = threading.Thread(target=scheduler.keepOrder)
    # scheduler.runThreadKeepOrder.start()
    scheduler.runThreadSchduler = threading.Thread(target=scheduler.schduling)
    scheduler.runThreadSchduler.start()
    return HttpResponse("startUp successful, Scheduler is Running "+time.asctime(time.localtime(time.time())))

def shutDown(request):
    global scheduler
    # if scheduler == None:
    #     return HttpResponse("nothing to shutDown "+time.asctime(time.localtime(time.time())))
    if not helper.hotelOn():
        return HttpResponse("nothing to shutDown " + time.asctime(time.localtime(time.time())))
    hotel = Hotel.objects.filter(endTime=0)
    hotel = hotel[0]
    hotel.isSchedulerRunning = 0
    hotel.endTime = time.time()
    hotel.save()
    #服务对象关机
    i = 1
    while i <= hotel.serveUnitNum:
        unit = ServerUnit.objects.filter(name=i)
        unit = unit[0]
        unit.state = 2
        unit.save()
        i += 1
    return HttpResponse("shutDown successful "+time.asctime(time.localtime(time.time())))

def checkRoomStatePage(request):
    return render(request,"inspect.html")

def checkRoomState(request):
    # print("in")
    roomNum=Hotel.objects.last().roomNum    #获取房间数
    list_Room=[]
    # 获取所有费率
    feeRates = Hotel.objects.last()
    feeRates = feeRates.feeRateL
    #现在时间
    now=time.time()
    #获取房间状态信息
    for i in range(1,roomNum+1):
        room=RoomState.objects.get(roomID=i)
        #空调状态
        if room.state==1 or room.state==3:
            state="wait"
        elif room.state==2:
            state="serving"
        else:
            state = "stop"
        #当前温度
        cur_temp=room.temp
        if state=="stop":
            targetTemp=0
            fan="null"
            feeRate="null"
            fee=0
            power=0
            duration=0
        else:
            request=RoomRequest.objects.filter(roomID=i).last()
            targetTemp=request.targetTemp
            fan = SPEED[request.speed + 1][1]
            # feeRate = feeRates[request.speed]
            fee=room.fee
            power=room.power
            # 空调最后一次关机时间
            stop_request=RoomRequest.objects.filter(roomID=i,speed=-1)#停止的请求
            if len(stop_request)==0:#系统第一次运行
                stop_time=0
            else:
               stop_time=stop_request.last().time
            requests=RoomRequest.objects.filter(roomID=i,time__gt=stop_time)#房间i从最后一次关机到现在的请求记录
            requests_id=requests.values_list("id",flat=True)
            serves=SchedulerLog.objects.filter(requestID__in=requests_id)#房间i从最后一次关机到现在，所有服务请求的调度记录
            # 计算服务时长，时间单位为s
            duration=0
            for record in serves:
                if record.endTime==0:
                    endtime=now
                else:
                    endtime=record.endTime
                duration+=(endtime-record.startTime)
                duration=int(duration)
        fee=round(fee,2)
        power=round(power,2)
        cur_temp=round(cur_temp,2)
        list_Room.append({"state":state,"Current_Temp":cur_temp,"Target_Temp":targetTemp,"Fan":fan,"FeeRate":feeRates,"Fee":fee,"Duration":duration,"Power":power})
    helper.helpLog()
    return JsonResponse(list_Room,safe=False)

