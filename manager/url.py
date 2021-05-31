from django.urls import path
from . import views
urlpatterns = [
    path('',views.page),
    path('QueryReport', views.queryReport),
    path('PrintReport', views.printReport),
]