from .compat import string_types
from .models import PRIORITY
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
