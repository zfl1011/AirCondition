from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import RoomState, RoomRequest
from inspector.models import Hotel,WaitQueue
import time
from common import helper
# Create your views here.
def selectRoom(request):
    return render(request, 'user_sr.html')
def index(request):
    ID = request.GET.get('RoomId')
    ID = int(ID)
    if not(ID > -1 or ID < 5):
        return HttpResponse("wrong room")
    ID = ID+1
    hotel = Hotel.objects.filter(endTime=0)
    hotel = hotel[0]
    if hotel.Mode==1:
        return render(request, 'user_c.html', {'id': ID,'dt':hotel.defaultTargetTemp,'lt':hotel.tempLimitLow,'ht':hotel.tempLimitHigh})
    return render(request, 'user_w.html', {'id': ID,'dt':hotel.defaultTargetTemp,'lt':hotel.tempLimitLow,'ht':hotel.tempLimitHigh})#TODO 房间号

def requestOn(request):
    if not helper.hotelOn():
        return HttpResponse("no service")
    #ps：由inspector-scheduler-orderkeeper改waitqueue 这里不管
    roomID = request.GET.get('RoomId')
    # temp = request.GET.get('CurrentRoomTemp')#客户端哪里有temp啊..
    print("requestOn:",roomID)
    room = RoomState.objects.filter(roomID=roomID)
    if len(room) == 0 or room[0].state != 0:#其实正常点网页就不会发生这种，但是直接输网址就会出问题
        return HttpResponse("no this room or already on")
    room = room[0]
    hotel = Hotel.objects.filter(endTime=0)
    hotel = hotel[0]
    roomID = int(roomID)
    if hotel.Mode == 1:
        print("!!!Mode==1")
        if roomID == 1:
            room.temp = 32
        elif roomID == 2:
            room.temp = 28
        elif roomID == 3:
            room.temp = 30
        elif roomID == 4:
            room.temp = 29
        elif roomID == 5:
            room.temp = 35
    else:
        if roomID == 1:
            room.temp = 10
        elif roomID == 2:
            room.temp = 15
        elif roomID == 3:
            room.temp = 18
        elif roomID == 4:
            room.temp = 12
        elif roomID == 5:
            room.temp = 14
    roomRequest = RoomRequest.objects.create(roomID=roomID, time=time.time(),temp = -1, targetTemp = hotel.defaultTargetTemp)
    roomRequest.save()
    room.state = 1
    room.plus = roomRequest.pk
    room.save()
    ret = "成功，目标温度"+str(roomRequest.targetTemp)+"风速"+str(roomRequest.speed)
    return HttpResponse(ret)
    # return render(request, 'userIndex.html')

def changeTargetTemp(request):
    if not helper.hotelOn():
        return HttpResponse("no service")
    roomID = request.GET.get('RoomId')
    temp = request.GET.get('TargetTemp')
    room = RoomState.objects.filter(roomID=roomID)
    if len(room) == 0 or room[0].state == 0:
        return HttpResponse("no room or requeston first")
    last = RoomRequest.objects.filter(roomID=roomID).order_by("-pk")
    print(int(last[0].targetTemp),temp)
    tmp = int(last[0].targetTemp)
    if tmp == int(temp):
        return HttpResponse("no change")
    # if time.time()-last[0].time<5:
    #     return HttpResponse("too fast")
    roomRequest = RoomRequest.objects.create(roomID=roomID, speed=last[0].speed,targetTemp=last[0].targetTemp)
    roomRequest.time = time.time()
    hotel = Hotel.objects.filter(endTime=0)
    hotel = hotel[0]
    str = "OK"
    if float(temp) > hotel.tempLimitHigh :
        # roomRequest.targetTemp = hotel.tempLimitHigh
        str = "too high"
    elif float(temp) < hotel.tempLimitLow:
        # roomRequest.targetTemp = hotel.tempLimitLow
        str = "too low"
    else:
        roomRequest.targetTemp = temp
    roomRequest.save()
    if room[0].state != 2:
        room[0].plus = roomRequest.pk
    room[0].save()
    return HttpResponse(str)

def changeFanTemp(request):
    if not helper.hotelOn():
        return HttpResponse("no service")
    roomID = request.GET.get('RoomId')
    speed = request.GET.get('FanSpeed')
    room = RoomState.objects.filter(roomID=roomID)
    if len(room) == 0 or room[0].state == 0:
        return HttpResponse("no room or requeston first")
    last = RoomRequest.objects.filter(roomID=roomID).order_by("-pk")
    if last[0].speed == speed:
        return HttpResponse("no change")
    # if time.time()-last[0].time<5:
    #     return HttpResponse("too fast")
    if room[0].state != 2:
        print("will change")
        roomRequest = RoomRequest.objects.create(time = time.time(),roomID=roomID, temp=-1, targetTemp=last[0].targetTemp)
        roomRequest.save()
        room[0].state = 1
        room[0].plus = roomRequest.pk
    else:
        roomRequest = RoomRequest.objects.create(time = time.time(),roomID=roomID, temp=0, targetTemp=last[0].targetTemp)
        roomRequest.save()
    str = "OK"
    if int(speed) > 2:
        # roomRequest.speed = 2
        str = "too fast"
    elif int(speed) < 0:
        # roomRequest.targetTemp = 0
        str = "too low"
    else:
        roomRequest.speed = speed

    roomRequest.save()
    room[0].save()
    return HttpResponse(str)

def requestOff(request):#费用没清零吧，必须下次开机前打账单
    if not helper.hotelOn():
        return HttpResponse("no service")
    roomID = request.GET.get('RoomId')
    room = RoomState.objects.filter(roomID=roomID)
    if len(room) == 0 or room[0].state == 0:
        return HttpResponse("no room or requeston first")
    roomRequest = RoomRequest.objects.create(roomID=roomID, time=time.time(), speed=-1)
    roomRequest.save()
    wq = WaitQueue.objects.get(roomID=roomID)
    wq.order = 0
    wq.save()
    room[0].state = 0
    room[0].plus = -1
    room[0].save()

    return HttpResponse(roomID+"号房空调已关机")

def requestFee(request):
    # if not helper.hotelOn():
    #     return HttpResponse("no service")
    roomID = request.GET.get('RoomId')
    # room = RoomState.objects.filter(roomID=roomID)
    # if len(room) == 0 :
    #     return HttpResponse("no such room ")
    # return HttpResponse(room[0].fee)
    room = RoomState.objects.get(roomID=roomID)
    return HttpResponse(room.fee)

def LogIn(request):
    RoomId=request.GET.get("room_id")
    CusId=request.GET.get("cus_name")
    room = RoomState.objects.get(roomID=RoomId)
    cus=RoomState.objects.get(cus_id=CusId)
    if len(CusId)!=18 or room.state!=0:
        return JsonResponse({"code": 1})
    if cus.roomID!=RoomId:
        return JsonResponse({"code": 2})
    room.cus_id=cus
    return JsonResponse({"code":0})

def SetUp(request):
    if not helper.hotelOn():
        return HttpResponse("no service")
    RoomId=request.GET.get('room_id')
    OnFlag=request.GET.get('on_flag')
    Mode=request.GET.get('mode')
    Speed=request.GET.get('speed')
    Temp=request.GET.get('temp_target')
    room = RoomState.objects.filter(roomID=RoomId)
    if len(room) == 0:  # 其实正常点网页就不会发生这种，但是直接输网址就会出问题
        return HttpResponse("no this room or already on")
    hotel = Hotel.objects.filter(endTime=0)
    hotel = hotel[0]
    if hotel.Mode!=Mode+1:
        return JsonResponse({"code":1})
    if int(OnFlag)==0 and room[0].state==0:
        room = room[0]
        roomID = int(RoomId)
        if hotel.Mode == 1:
            print("!!!Mode==1")
            if roomID == 1:
                room.temp = 32
            elif roomID == 2:
                room.temp = 28
            elif roomID == 3:
                room.temp = 30
            elif roomID == 4:
                room.temp = 29
            elif roomID == 5:
                room.temp = 35
        else:
            if roomID == 1:
                room.temp = 10
            elif roomID == 2:
                room.temp = 15
            elif roomID == 3:
                room.temp = 18
            elif roomID == 4:
                room.temp = 12
            elif roomID == 5:
                room.temp = 14
        roomRequest = RoomRequest.objects.create(roomID=roomID, time=time.time(), temp=-1,
                                                 targetTemp=hotel.defaultTargetTemp)
        roomRequest.save()
        room.state = 1
        room.plus = roomRequest.pk
        room.save()
    last = RoomRequest.objects.filter(roomID=roomID).order_by("-pk")
    roomRequest = RoomRequest.objects.create(roomID=roomID, speed=Speed, targetTemp=Temp,time=time.time())
    if room[0].state != 2:
        if Temp!=last[0].targetTemp:
            room[0].plus = roomRequest.pk
        if Speed!=last[0].speed:
            roomRequest.temp = -1
            roomRequest.save()
            room[0].state = 1
            room[0].plus = roomRequest.pk
    else:
        roomRequest.temp = 0
        roomRequest.save()
    roomRequest.save()
    room[0].save()
    return JsonResponse({"code":0})

def LogOut(request):
    if not helper.hotelOn():
        return HttpResponse("no service")
    RoomId = request.GET.get('room_id')
    room = RoomState.objects.filter(roomID=RoomId)
    if len(room) == 0 or room[0].state == 0:
        return HttpResponse("no room or requeston first")
    roomRequest = RoomRequest.objects.create(roomID=roomID, time=time.time(), speed=-1)
    roomRequest.save()
    wq = WaitQueue.objects.get(roomID=roomID)
    wq.order = 0
    wq.save()
    room[0].state = 0
    room[0].plus = -1
    room[0].save()
    return JsonResponse({"cost":room[0].fee})

def Monitor(request):
    RoomId = request.GET.get('room_id')
    room = RoomState.objects.get(roomID=RoomId)
    hotel = Hotel.objects.filter(endTime=0)
    hotel = hotel[0]
    if room.state == 0:
        NowTemp=0
        TargetTemp=0
        Cost=0
        Power=0
        Mode=0
        Speed=0
    else:
        cur_temp = room.temp
        request = RoomRequest.objects.filter(roomID=RoomId).last()
        TargetTemp = request.targetTemp
        Speed= request.speed
        fee = room.fee
        power = room.power
        Cost = round(fee, 2)
        Power = round(power, 2)
        CurTemp = round(cur_temp, 2)
        Mode=hotel.Mode-1
    return JsonResponse({"temp_now":NowTemp,"temp_target":TargetTemp,"cost":Cost,"power":Power,"mode":Mode,"speed":Speed})