from django.urls import path
from . import views
urlpatterns = [
    path('', views.receptionMain),
    path('RDR', views.RDRPage),
    path('CreateRDR', views.createRDR),
    path('PrintRDR', views.printRDR),
    path('CreateInvoice', views.createInvoice),
    path('PrintInvoice', views.printInvoice),
]