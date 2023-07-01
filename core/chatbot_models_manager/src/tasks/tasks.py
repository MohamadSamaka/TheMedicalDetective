from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.cache import cache


@shared_task
def set_cancel_flag(id, val):
    cache.set(
        id,
        {'cancel_flag': val},
        timeout=60*60
    )