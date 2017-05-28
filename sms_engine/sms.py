from django.db.models import Q
from django.utils import timezone

from .models import SMS, PRIORITY, STATUS
from .settings import get_log_level, get_available_backends
from .utils import parse_priority


def create(to=None, message="", scheduled_time=None, priority=None,
           commit=True, backend=""):
    """
        A function to create smses from supplied keyword arguments.
    """
    priority = parse_priority(priority)
    status = None if priority == PRIORITY.now else STATUS.queued

    sms = SMS(
        to=to, message=message, scheduled_time=scheduled_time,
        status=status, priority=priority, backend_alias=backend
    )

    if commit:
        sms.save()

    return sms


def send(to=None, message="", scheduled_time=None, priority=None,
         commit=True, backend="", log_level=None):

    priority = parse_priority(priority)

    if log_level is None:
        log_level = get_log_level()

    if not commit and priority == PRIORITY.now:
        raise ValueError("send_many() can't be used with priority = 'now'")

    if backend and backend not in get_available_backends().keys():
        raise ValueError('%s is not a valid backend alias' % backend)

    sms = create(to, message, scheduled_time,
                 priority, commit, backend)

    if priority == PRIORITY.now:
        sms.dispatch(log_level=log_level)

    return sms


def get_queued():
    return SMS.objects.filter(status=STATUS.queued) \
              .filter(Q(scheduled_time__lte=timezone.now()) | Q(scheduled_time=None))
