from django.shortcuts import render
from django.http import HttpResponse
from .models import Report
import time

from django.http import HttpResponse, JsonResponse, FileResponse
from django.core import serializers


# Create your views here.
def page(request):
    return render(request,"manager.html")


def queryReport(request):
    if (request.method == 'POST'):
        print("the POST method")
        p = request.POST
        # postBody = request.body
        # print(concat)
        # print(type(postBody))
        # print(postBody)
        roomList = p["roomList"]
        idList = []
        for r in roomList:
            if r!=",":
                idList.append(r)
        type = p["type"]
        date = p["stime"]
        stime = time.mktime(time.strptime(date,"%Y.%m.%d-%H"))
        if stime > time.time():
            stime = time.time() # return HttpResponse("wrong start time")
        nametype = "D"
        if type == 1:
            nametype = "W"
        elif type == 2:
            nametype = "M"
        elif type == 3 :
            nametype = "Y"
        postion = "File_Report/" + time.strftime("%Y-%m-%d",time.localtime(time.time()))+"-"+str(len(Report.object.all())+1) +"-"+nametype+ ".xlsx"
        print(postion)
        Report.object.create(time=round(time.time()), roomList=idList, type=type, date=date, position=postion)
        list_report = Report.object.creatReport(stime, idList, type , nametype)
        return JsonResponse(list_report,safe=False)
    else :
        return HttpResponse("wrong access")

def printReport(request):
    r = Report.object.all().last()
    p = r.position
    file = open(p, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    # file_name下载下来保存的文件名字
    file_name = p[12:]
    print(file_name)
    content_dis = 'attachment;filename="' + file_name + '"'
    response['Content-Disposition'] = content_dis
    return response

