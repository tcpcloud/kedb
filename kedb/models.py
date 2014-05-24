
import os
import re
from datetime import datetime
from logging import getLogger

from django.db import models
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

LEVEL_CHOICES = (
    ("l1", u"Level 1"),
    ("l2", u"Level 2"),
)

SEVERITY_CHOICES = (
    ("int", u"Internal"),
    ("sla999", u"SLA 99.9"),
    ("sla9999", u"SLA 99.99"),
)

OWNERSHIP_CHOICES = (
    ("cloudlab", u"Cloudlab"),
    ("network", u"network"),
)

ENGINE_CHOICES = (
    ("salt", u"Salt call"),
    ("jenkins", u"Jenkins job"),
)

class KnownError(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'), blank=True)
    check = models.CharField(max_length=255, verbose_name=_('sensu check'),)
    output_pattern = models.CharField(max_length=255, verbose_name=_('output pattern'))
    level = models.CharField(max_length=55, verbose_name=_('level'), default='level1', choices=LEVEL_CHOICES)
    severity = models.CharField(max_length=55, verbose_name=_('severity'), default='medium', choices=SEVERITY_CHOICES)
    ownership = models.CharField(max_length=55, verbose_name=_('ownership'), default='cloudlab', choices=OWNERSHIP_CHOICES)

    @staticmethod
    def reg(string, IGNORECASE=True):
        """warpper for compile regular"""
        reg = None
        try:
            if IGNORECASE:
                reg = re.compile(string, re.IGNORECASE)
            else:
                reg = re.compile(string)
        except Exception, e:
            raise e
        return reg

    @classmethod
    def find_by_event(cls, check, output):
        instances = KnownError.objects.filter(check=check)
        final_instance = None
        for instance in instances:
            reg = KnownError.reg(instance.output_pattern)
            if reg:
                if len(reg.findall(output)) > 0:
                    final_instance = instance
        return final_instance

    class Meta:
        verbose_name = _("known error")
        verbose_name_plural = _("known errors")

class Workaround(models.Model):
    known_error = models.ForeignKey(KnownError, verbose_name=_('known error'), related_name='workarounds')
    description = models.TextField(verbose_name=_('description'), blank=True)
    temporary = models.BooleanField(max_length=255, verbose_name=_('temporary'))
    engine = models.CharField(max_length=255, verbose_name=_('engine'), default='salt', choices=ENGINE_CHOICES)
    action = models.TextField(verbose_name=_('description'), blank=True)

    @property
    def error_detail(self):
        return self.known_error

    class Meta:
        verbose_name = _("workaround")
        verbose_name_plural = _("workarounds")
