import datetime

from django import template

register = template.Library()


def utc_timestamp(t):
    try:
        # assume, that timestamp is given in seconds with decimal point
        ts = float(timestamp)
    except ValueError:
        return None
    return datetime.datetime.fromtimestamp(ts)


register.filter(utc_timestamp)
