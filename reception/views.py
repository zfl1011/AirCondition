from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse
from .models import RDR,Invoice
from user.models import RoomState, RoomRequest
from inspector.models import SchedulerLog
# Create your views here.
#计费在结算后清空 roomstate也要改0 发一个requestOff
from common import helper
import time

def receptionMain(request):
    return render(request,"reception.html")

def RDRPage(request):
    roomID = request.GET.get('RoomId')
    dateIn = request.GET.get('date_in')
    dateOut = request.GET.get('date_out')
    return render(request, "reception_RDR.html", {"id":roomID,"in":dateIn,"out":dateOut})

def createRDR(request):
    # if not helper.hotelOn():
    #     return HttpResponse("no service")
    Time=time.time()
    roomID = request.GET.get('RoomId')
    dateIn=request.GET.get('date_in')
    dateOut=request.GET.get('date_out')
    timeIn=time.mktime(time.strptime(dateIn,"%Y.%m.%d-%H"))
    timeOut=time.mktime(time.strptime(dateOut, "%Y.%m.%d-%H"))
    postion="File_RDR/"+ roomID+"_"+time.strftime("%Y%m%d")+"_RDR.xlsx"
    RDR.object.create(time=Time,roomID=roomID,timeIn=timeIn,timeOut=timeOut,position=postion,isPrint=0)
    list_RDR=RDR.object.creatRDR(time,roomID,timeIn,timeOut)
    return JsonResponse(list_RDR,safe=False)

def printRDR(request):
    # if not helper.hotelOn():
    #     return HttpResponse("no service")
    roomID = request.GET.get('RoomId')
    rdr=RDR.object.filter(roomID=roomID).last()
    rdr.isPrint=1
    rdr.save()
    #position为详单位置
    position=RDR.object.filter(roomID=roomID).last().position
    file = open(position, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    # file_name下载下来保存的文件名字
    Time=rdr.time
    file_name=roomID+"_" + time.strftime("%Y%m%d",time.localtime(Time)) +"_RDR.xlsx"
    content_dis = 'attachment;filename="' + file_name + '"'
    response['Content-Disposition'] = content_dis
    return response

def createInvoice(request):
    # if not helper.hotelOn():
    #     return HttpResponse("no service")
    Time=time.time()
    roomID = request.GET.get('RoomId')
    dateIn=request.GET.get('date_in')
    dateOut=request.GET.get('date_out')
    timeIn=time.mktime(time.strptime(dateIn,"%Y.%m.%d-%H"))
    timeOut=time.mktime(time.strptime(dateOut, "%Y.%m.%d-%H"))
    logs = SchedulerLog.objects.filter(roomID=roomID, startTime__range=[timeIn, timeOut])
    fee=0.0
    for record in logs:
        fee=fee+record.fee
    roomstate=RoomState.objects.get(roomID=roomID)
    roomstate.state = 0
    #记录request
    RoomRequest.objects.create(roomID=roomID, time=time.time(), speed=-1)
    # 计费在结算后清空 roomstate也要改0
    roomstate.fee=0
    roomstate.save()

    Invoice.objects.create(time=Time,roomID=roomID,timeIn=timeIn,timeOut=timeOut,fee=fee,isPrint=0)
    filename = roomID + "_" + time.strftime("%Y%m%d",time.localtime(Time)) + "_Invoice.txt"
    position = "File_Invoice/" + filename
    file = open(position, "w")
    file.write("RoomId:" + roomID+'\n')
    file.write("Total_Fee:" + str(fee)+'\n')
    file.write("date_in:" + dateIn + ':00\n')
    file.write("date_out:" + dateOut + ':00\n')
    file.close()
    return JsonResponse({"RoomId":roomID,"Total_Fee":fee,"date_in":dateIn+':00',"date_out":dateOut+':00'})

def printInvoice(request):
    # if not helper.hotelOn():
    #     return HttpResponse("no service")
    roomID = request.GET.get('RoomId')
    print(roomID)
    invoice=Invoice.objects.filter(roomID=roomID).last()
    invoice.isPrint=1
    invoice.save()
    Time=invoice.time
    position="File_Invoice/" + roomID + "_" + time.strftime("%Y%m%d",time.localtime(Time)) + "_Invoice.txt"
    file = open(position, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    # file_name下载下来保存的文件名字
    file_name=roomID+"_" + time.strftime("%Y%m%d",time.localtime(Time)) +"_Invoice.txt"
    content_dis = 'attachment;filename="' + file_name + '"'
    response['Content-Disposition'] = content_dis
    return response