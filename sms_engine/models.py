import random

from collections import namedtuple

from django.db import models
from django.utils.six import python_2_unicode_compatible, text_type
from django.utils.translation import ugettext_lazy as _

from .settings import get_log_level, get_backend


PRIORITY = namedtuple('PRIORITY', 'low medium high now')._make(range(4))
STATUS = namedtuple('STATUS', 'sent failed queued')._make(range(3))


@python_2_unicode_compatible
class SMS(models.Model):
    """
        A model to hold SMS information
    """

    PRIORITY = [(PRIORITY.low, _("low")), (PRIORITY.medium, _("medium")),
                (PRIORITY.high, _("high")), (PRIORITY.now, _("now"))]
    STATUS = [(STATUS.sent, _("sent")), (STATUS.failed, _("failed")),
              (STATUS.queued, _("queued"))]

    to = models.CharField(_("The destination number"), max_length=20)
    message = models.TextField(_("Content of sms"))
    created = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(
        _("Status"),
        choices=STATUS,
        blank=True, null=True)
    priority = models.PositiveSmallIntegerField(_("Priority"),
                                                choices=PRIORITY,
                                                blank=True, null=True)
    scheduled_time = models.DateTimeField(_('The scheduled sending time'),
                                          blank=True, null=True, db_index=True)
    backend_alias = models.CharField(_('Backend alias'), blank=True, default='',
                                     max_length=64)
    description = models.CharField(max_length=256, blank=True, default='')
    transaction_id = models.CharField(max_length=256, blank=True, default='')
    start_of_delivery_window = models.TimeField(blank=True, null=True)
    end_of_delivery_window = models.TimeField(blank=True, null=True)

    class Meta:
        app_label = 'sms_engine'

    def __str__(self):
        return u'%s' % self.to

    def dispatch(self, log_level=None, commit=True):
        """
        Method that send out the sms
        """
        if log_level is None:
            log_level = get_log_level()

        try:
            backend = get_backend(self.backend_alias)
            self.transaction_id = backend.send_message(self)

            message = ''
            status = STATUS.sent
            self.status = status
            exception_type = ''
        except Exception as e:
            message = e
            status = STATUS.failed
            self.status = status
            exception_type = type(e).__name__

            if not commit:
                raise

        if commit:
            self.save()

            # If log level is 0, log nothing, 1 only logs failures
            # and 2 means log both successes and failures
            if log_level == 1 and status == STATUS.failed:
                self.logs.create(status=status, message=message,
                                 exception_type=exception_type)
            elif log_level == 2:
                self.logs.create(status=status, message=message,
                                 exception_type=exception_type)

        return status


@python_2_unicode_compatible
class Log(models.Model):
    """
    A model to record sending sms sending activities.
    """

    STATUS_CHOICES = [(STATUS.sent, _("sent")), (STATUS.failed, _("failed"))]

    sms = models.ForeignKey(SMS, editable=False, related_name='logs',
                            on_delete=models.CASCADE, verbose_name=_('SMS'))
    date = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(_('Status'), choices=STATUS_CHOICES)
    exception_type = models.CharField(_('Exception type'), max_length=255, blank=True)
    message = models.TextField(_('Message'))

    class Meta:
        app_label = 'sms_engine'

    def __str__(self):
        return text_type(self.date)


@python_2_unicode_compatible
class Backend(models.Model):
    alias = models.CharField(max_length=255)
    PRIORITY = namedtuple('PRIORITY', 'high normal low')._make(range(3))
    PRIORITY_CHOICES = [(PRIORITY.high, _("high")), (PRIORITY.normal, _("normal")),
                        (PRIORITY.low, _("low"))]
    priority = models.IntegerField(_("Priority"), choices=PRIORITY_CHOICES, default=PRIORITY.normal)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'sms_engine'

    def __str__(self):
        return self.alias

    def save(self, *args, **kwargs):
        super(Backend, self).save(*args, **kwargs)
        from sms_engine import cached_backend
        cached_backend.delete()

    @classmethod
    def flatten(cls, backend_dict, cache=True, min_backends=3):
        """ Return flattened list of backend alias to try in order.
            * This generates `min_backeds` amount of backends.
            * Backends will randomly be repeated until min_backends reach
            * Backends with same priority are shuffled
        """
        # Shuffle multiple backends
        # List[str]
        flattened_backends = []
        for key in [cls.PRIORITY.high, cls.PRIORITY.normal, cls.PRIORITY.low]:
            random.shuffle(backend_dict[key])
            flattened_backends += backend_dict[key]

        # Repeat some backends if backends are properly setup and less than min_backends
        while flattened_backends and len(flattened_backends) < min_backends:
            flattened_backends += random.sample(flattened_backends, 1)

        return flattened_backends
