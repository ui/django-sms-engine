from django.contrib import admin

from .models import SMS, Log, Backend


class LogInline(admin.TabularInline):
    model = Log


class SMSAdmin(admin.ModelAdmin):
    list_display = ('to', 'status', 'priority', 'backend_alias', 'created')
    search_fields = ('to', 'description',)
    inlines = [LogInline]


class BackendAdmin(admin.ModelAdmin):
    list_display = ('alias', 'priority')


admin.site.register(SMS, SMSAdmin)
admin.site.register(Backend, BackendAdmin)