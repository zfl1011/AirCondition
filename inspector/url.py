from django.urls import path
from . import views
urlpatterns = [
    path('', views.index),
    path('powerOn', views.powerOn),
    path('setPara', views.setPara),
    path('startUp', views.startUp),
    path('shutDown', views.shutDown),
    path('page',views.checkRoomStatePage),
    path('CheckRoomState', views.checkRoomState),
]