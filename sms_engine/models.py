from collections import namedtuple

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .compat import text_type


PRIORITY = namedtuple('PRIORITY', 'low medium high now')._make(range(4))
STATUS = namedtuple('STATUS', 'sent failed queued')._make(range(3))


@python_2_unicode_compatible
class SMS(models.Model):
    """
        A model to hold SMS information
    """

    PRIORITY_CHOICES = [(PRIORITY.low, _("low")), (PRIORITY.medium, _("medium")),
                        (PRIORITY.high, _("high")), (PRIORITY.now, _("now"))]
    STATUS_CHOICES = [(STATUS.sent, _("sent")), (STATUS.failed, _("failed")),
                      (STATUS.queued, _("queued"))]

    to = models.CharField(_("The destination number"), max_length=20)
    message = models.TextField(_("Content of sms"))
    created = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(
        _("Status"),
        choices=STATUS_CHOICES, db_index=True,
        blank=True, null=True)
    priority = models.PositiveSmallIntegerField(_("Priority"),
                                                choices=PRIORITY_CHOICES,
                                                blank=True, null=True)
    scheduled_time = models.DateTimeField(_('The scheduled sending time'),
                                          blank=True, null=True, db_index=True)

    class Meta:
        app_label = 'sms_engine'

    def __str__(self):
        return u'%s' % self.to


@python_2_unicode_compatible
class Log(models.Model):
    """
    A model to record sending sms sending activities.
    """

    STATUS_CHOICES = [(STATUS.sent, _("sent")), (STATUS.failed, _("failed"))]

    sms = models.ForeignKey(SMS, editable=False, related_name='smses',
                            verbose_name=_('SMS'))
    date = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(_('Status'), choices=STATUS_CHOICES)
    exception_type = models.CharField(_('Exception type'), max_length=255, blank=True)
    message = models.TextField(_('Message'))

    class Meta:
        app_label = 'sms_engine'

    def __str__(self):
        return text_type(self.date)
