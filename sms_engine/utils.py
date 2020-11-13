import csv
from datetime import date
from io import StringIO
from typing import Tuple

from .compat import string_types
from .models import PRIORITY, SMS
from .settings import get_default_priority


def parse_priority(priority):
    if priority is None:
        priority = get_default_priority()
    # If priority is given as a string, returns the enum representation
    if isinstance(priority, string_types):
        priority = getattr(PRIORITY, priority, None)

        if priority is None:
            raise ValueError('Invalid priority, must be one of: %s' %
                             ', '.join(PRIORITY._fields))
    return priority


def split_smss(smss, split_count=1):
    # Group smss into X sublists
    # taken from http://www.garyrobinson.net/2008/04/splitting-a-pyt.html
    if list(smss):
        return [smss[i::split_count] for i in range(split_count)]


def get_monthly_csv_raw_data(start: date, end: date) -> StringIO:
    smses = SMS.objects.filter(created__date__range=(start, end))
    csv_buffer = StringIO()

    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow([
        'Destination', 'Content', 'Description', 'Backend'
    ])
    for sms in smses:
        csv_writer.writerow([
            sms.to, sms.message, sms.description, sms.backend_alias
        ])
    return csv_buffer


def parse_sms_raw_data_csv(file: StringIO, otp_descriptions: list) -> Tuple[StringIO, StringIO]:
    # count otp and non otp sms
    reader = csv.DictReader(file)

    otp_csv_buffer = StringIO()
    non_otp_csv_buffer = StringIO()

    otp_sms_writer = csv.writer(otp_csv_buffer)
    otp_sms_writer.writerow(reader.fieldnames)

    non_otp_sms_writer = csv.writer(non_otp_csv_buffer)
    non_otp_sms_writer.writerow(reader.fieldnames)

    for row in reader:
        if row['Description'] in otp_descriptions:
            otp_sms_writer.writerow(row.values())
        else:
            non_otp_sms_writer.writerow(row.values())
    return otp_csv_buffer, non_otp_csv_buffer
