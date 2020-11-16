from datetime import datetime

from django import forms
from django.forms.widgets import DateInput
from django.utils import timezone


class PastDateField(forms.DateField):

    today = timezone.localdate()
    # ignore type, keep using DateInput
    widget = DateInput(attrs={'max': today})  # type: ignore

    def clean(self, value):
        # convert to date object
        date = super(PastDateField, self).clean(value)

        # Convert date and assign to self.end_date
        time = datetime(date.year, date.month, date.day, hour=23,
                        minute=59, second=59, microsecond=999999)

        localtime = timezone.make_aware(time)
        if localtime.date() > timezone.localdate():
            raise forms.ValidationError("Date is not valid")

        self.end_date = localtime
        return localtime
