from django.contrib import admin

from .models import SMS, Log


class LogInline(admin.TabularInline):
    model = Log


class SMSAdmin(admin.ModelAdmin):
    list_display = ('to', 'created', 'status', 'backend_alias')
    search_fields = ('to', 'description')
    inlines = [LogInline]

admin.site.register(SMS, SMSAdmin)
