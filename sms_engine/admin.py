from django.contrib import admin

from .models import SMS, Log

admin.site.register(SMS)
admin.site.register(Log)
