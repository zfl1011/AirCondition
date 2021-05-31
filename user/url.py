from django.urls import path
from . import views
urlpatterns = [
    path('SelectRoom', views.selectRoom),
    path('',views.index),
    path('RequestOn', views.requestOn),
    path('ChangeTargetTemp', views.changeTargetTemp),
    path('ChangeFanSpeed', views.changeFanTemp),#名字错了，但又不能改。。
    path('RequestOff', views.requestOff),
    path('RequestFee', views.requestFee),
    #TODO 估计还有个获取温度的，在发送requeston之前问，或者干脆不要这个参数了，然后后端有一个回温的一直运行
]