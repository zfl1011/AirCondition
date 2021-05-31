from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Hotel)
admin.site.register(WaitQueue)
admin.site.register(ServerUnit)
admin.site.register(SchedulerLog)