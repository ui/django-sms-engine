from django.contrib import admin

from .models import SMS, Log


class LogInline(admin.TabularInline):
    model = Log


class SMSAdmin(admin.ModelAdmin):
    search_fields = ('to', 'description')
    inlines = [LogInline]

admin.site.register(SMS, SMSAdmin)
