from .compat import string_types
from .models import PRIORITY, SMS
from .settings import get_default_priority

from typing import Any


def parse_priority(priority: str) -> str:
    if priority is None:
        priority = get_default_priority()
    # If priority is given as a string, returns the enum representation
    if isinstance(priority, string_types):
        priority = getattr(PRIORITY, priority, None)

        if priority is None:
            raise ValueError('Invalid priority, must be one of: %s' %
                             ', '.join(PRIORITY._fields))
    return priority


def split_smss(smss: list, split_count: int = 1) -> Any:
    # Group smss into X sublists
    # taken from http://www.garyrobinson.net/2008/04/splitting-a-pyt.html
    if list(smss):
        return [smss[i::split_count] for i in range(split_count)]


def get_sms_usage(start_date: str, end_date: str) -> dict:
    if start_date > end_date:
        raise ValueError('`start` must be earlier than `end`')

    smss = SMS.objects.filter(scheduled_time__range=[start_date, end_date])

    result_sms_usage: dict = {}

    for sms in smss:
        if sms.backend_alias not in result_sms_usage:
            if sms.status == 0:
                result_sms_usage[sms.backend_alias] = {"total": 1, "succes": 1, "failed": 0}
            else:
                result_sms_usage[sms.backend_alias] = {"total": 1, "succes": 0, "failed": 1}
        else:
            result_sms_usage[sms.backend_alias]["total"] += 1
            if sms.status == 0:
                result_sms_usage[sms.backend_alias]["succes"] += 1
            else:
                result_sms_usage[sms.backend_alias]["failed"] += 1

    return result_sms_usage
