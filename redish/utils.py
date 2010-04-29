import time
from datetime import datetime


def maybe_list(value):
    if hasattr(value, "__iter__"):
        return value
    if value is None:
        return []
    return [value]


def mkey(names):
    return ":".join(maybe_list(names))


def dt_to_timestamp(dt):
    """Convert :class:`datetime` to UNIX timestamp."""
    return time.mktime(dt.timetuple())

def maybe_datetime(timestamp):
    """Convert datetime to timestamp, only if timestamp
    is a datetime object."""
    if isinstance(timestamp, datetime):
        return dt_to_timestamp(timestamp)
    return timestamp
