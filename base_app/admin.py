from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Booking)
admin.site.register(Transaction)
admin.site.register(Profile)
admin.site.register(CheckStatusLog)
admin.site.register(Tickets)