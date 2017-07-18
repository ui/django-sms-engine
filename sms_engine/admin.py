from django.contrib import admin

from .models import SMS, Log


class LogInline(admin.TabularInline):
    model = Log


class SMSAdmin(admin.ModelAdmin):
    inlines = [LogInline]

admin.site.register(SMS, SMSAdmin)
