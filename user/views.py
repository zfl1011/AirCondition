from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import RoomState, RoomRequest
from inspector.models import Hotel,WaitQueue
import time
import random
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

def LogIn(request):
    RoomId=request.GET.get("room_id")
    CusId=request.GET.get("cus_name")
    RoomId=int(RoomId)
    room = RoomState.objects.get(roomID=RoomId)
    cus=RoomState.objects.filter(cus_id=CusId)
    if len(CusId)!=18 or room.state!=0:
        return JsonResponse({"code": 1})
    if cus.count()!=0 and int(cus[0].roomID)!=RoomId :
        return JsonResponse({"code": 2})
    room.cus_id=CusId
    room.save()
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
    Mode=int(Mode)
    if hotel.Mode!=Mode+1:
        return JsonResponse({"code":1})
    if int(OnFlag)==0 and room[0].state==0:
        roomID = int(RoomId)
        if hotel.Mode == 1:
            print("!!!Mode==1")
            room[0].temp = random.randint(25,35)
        else:
            room[0].temp = random.randint(15,25)

        roomRequest = RoomRequest.objects.create(roomID=roomID, time=time.time(), temp=-1,
                                                 targetTemp=hotel.defaultTargetTemp)
        roomRequest.save()
        room[0].state = 1
        room[0].plus = roomRequest.pk
        room[0].save()
    roomID = int(RoomId)
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
    roomID = int(RoomId)
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
        CurTemp=0
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
    return JsonResponse({"temp_now":CurTemp,"temp_target":TargetTemp,"cost":Cost,"power":Power,"mode":Mode,"speed":Speed})