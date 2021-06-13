from django.urls import path
from . import views
urlpatterns = [
    path('SelectRoom', views.selectRoom),
    path('', views.index),
    path('client_login', views.LogIn),
    path('client_setup', views.SetUp),
    path('client_logout', views.LogOut),
    path('client_monitor', views.Monitor),
]