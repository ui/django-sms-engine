from .fields import PastDateField


class BaseReportFilter(forms.Form):
    start_date = PastDateField()
    end_date = PastDateField()

    def clean(self):
        data = super(BaseReportFilter, self).clean()
        if self.errors:
            return data

        start_date = data['start_date']
        end_date = data['end_date']
        diff = (end_date - start_date).days

        if start_date > end_date:
            error = forms.ValidationError('End date should be greater than start date',
                                          code="invalid_end_date")
            self.add_error('end_date', error)
        elif diff > 30:
            error = forms.ValidationError(
                "Maximum range date is 30 days", code="maximum_date_range_exceeded"
            )
            self.add_error('end_date', error)

        return data
