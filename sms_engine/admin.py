from django.conf.urls import url
from django.contrib import admin
from django.shortcuts import render

from .forms import BaseReportFilter
from .models import SMS, Log
from .utils import get_monthly_csv_raw_data, generate_zip_response


class LogInline(admin.TabularInline):
    model = Log


class SMSAdmin(admin.ModelAdmin):
    list_display = ('to', 'status', 'priority', 'backend_alias', 'created')
    search_fields = ('to', 'description',)
    inlines = [LogInline]

    def get_urls(self):
        urls = super(SMSAdmin, self).get_urls()
        custom_urls = [
            url(r'^exports$', self.exports, name='exports'),
        ]
        return custom_urls + urls

    def exports(self, request):
        form = BaseReportFilter(data=request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                start_date = form.cleaned_data.get('start_date')
                end_date = form.cleaned_data.get('end_date')
                csv_buffer = get_monthly_csv_raw_data(start_date, end_date)
                format_date = "%Y-%m-%d"
                filename = 'sms-{}-{}'.format(start_date.strftime(format_date), end_date.strftime(format_date))
                return generate_zip_response(csv_buffer, filename)

        context = {
            'form': form
        }

        return render(request, 'admin/form.html', context)


admin.site.register(SMS, SMSAdmin)
