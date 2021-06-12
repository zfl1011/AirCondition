from django.urls import path
from . import views
urlpatterns = [
    path('SelectRoom', views.selectRoom),
    path('', views.index),
    path('RequestOn', views.requestOn),
    path('ChangeTargetTemp', views.changeTargetTemp),
    path('ChangeFanSpeed', views.changeFanTemp),#名字错了，但又不能改。。
    path('RequestOff', views.requestOff),
    path('RequestFee', views.requestFee),

    path('client_login', views.LogIn),
    path('client_setup', views.SetUp),
    path('client_logout', views.LogOut),
    path('client_monitor', views.Monitor),
]