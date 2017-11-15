from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

from django.conf import settings
from django.db import connection as db_connection
from django.db.models import Q
from django.utils import timezone

from .logutils import setup_loghandlers
from .models import SMS, PRIORITY, STATUS, Log
from .settings import get_log_level, get_available_backends
from .utils import parse_priority, split_smss


logger = setup_loghandlers("INFO")


def create(to=None, message="", description="", scheduled_time=None, priority=None,
           commit=True, backend=""):
    """
        A function to create smses from supplied keyword arguments.
    """
    priority = parse_priority(priority)
    status = None if priority == PRIORITY.now else STATUS.queued

    if backend not in get_available_backends().keys():
        raise ValueError('%s is not a valid backend alias' % backend)

    sms = SMS(
        to=to, message=message, scheduled_time=scheduled_time,
        status=status, priority=priority, backend_alias=backend,
        description=description
    )

    if commit:
        sms.save()

    return sms


def send(to=None, message="", description="", scheduled_time=None, priority=None,
         commit=True, backend="", log_level=None):

    priority = parse_priority(priority)

    if log_level is None:
        log_level = get_log_level()

    if not commit and priority == PRIORITY.now:
        raise ValueError("send_many() can't be used with priority = 'now'")

    sms = create(to, message, description, scheduled_time,
                 priority, commit, backend)

    if priority == PRIORITY.now:
        sms.dispatch(log_level=log_level)

    return sms


def get_queued():
    limit = settings.SMS_ENGINE.get('BATCH_SIZE', 50)
    return SMS.objects.filter(status=STATUS.queued) \
              .filter(Q(scheduled_time__lte=timezone.now()) | Q(scheduled_time=None))[:limit]


def send_queued(processes=1, log_level=None):
    """
    Sends out all queued smss that has scheduled_time less than now or None
    """
    queued_smss = get_queued()
    total_sent, total_failed = 0, 0
    total_sms = len(queued_smss)

    logger.info('Started sending %s sms with %s processes.' %
                (total_sms, processes))

    if log_level is None:
        log_level = get_log_level()

    if queued_smss:

        # Don't use more processes than number of sms
        if total_sms < processes:
            processes = total_sms

        if processes == 1:
            total_sent, total_failed = _send_bulk(queued_smss,
                                                  uses_multiprocessing=False,
                                                  log_level=log_level)
        else:
            sms_lists = split_smss(queued_smss, processes)
            pool = Pool(processes)
            results = pool.map(_send_bulk, sms_lists)
            total_sent = sum([result[0] for result in results])
            total_failed = sum([result[1] for result in results])
    message = '%s sms attempted, %s sent, %s failed' % (
        total_sms,
        total_sent,
        total_failed
    )
    logger.info(message)
    return (total_sent, total_failed)


def _send_bulk(smss, uses_multiprocessing=True, log_level=None, threads=4):
    # Multiprocessing does not play well with database connection
    # Fix: Close connections on forking process
    # https://groups.google.com/forum/#!topic/django-users/eCAIY9DAfG0
    if uses_multiprocessing:
        db_connection.close()

    if log_level is None:
        log_level = get_log_level()

    sent_smses = []
    failed_smses = []
    sms_count = len(smss)


    logger.info('Process started, sending %s sms' % sms_count)

    def send(sms):
        try:
            sms.dispatch(log_level=log_level, commit=False)
            sent_smses.append(sms)
            logger.debug('Successfully sent sms #%d' % sms.id)
        except Exception as e:
            logger.debug('Failed to send sms #%d' % sms.id)
            failed_smses.append((sms, e))

    number_of_threads = min(threads, sms_count)
    pool = ThreadPool(number_of_threads)

    pool.map(send, smss)
    pool.close()
    pool.join()
    pool.terminate()

    # update statuses of sent and failed_smses
    for sms in sent_smses:
        sms.save()

    for (sms, _) in failed_smses:
        sms.save()

    if log_level >= 1:
        logs = []
        for (sms, exception) in failed_smses:
            logs.append(
                Log(sms=sms, status=STATUS.failed,
                    message=str(exception),
                    exception_type=type(exception).__name__)
            )

        if logs:
            Log.objects.bulk_create(logs)

    if log_level == 2:
        logs = []
        for sms in sent_smses:
            logs.append(Log(sms=sms, status=STATUS.sent))

        if logs:
            Log.objects.bulk_create(logs)

    sent_count = len(sent_smses)
    failed_count = len(failed_smses)
    logger.info('Process finished, %s attempted, %s sent, %s failed' %
                (sms_count, sent_count, failed_count))

    return (sent_count, failed_count)
