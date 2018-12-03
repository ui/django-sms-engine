from django.conf import settings
from django.core.cache import cache as dj_cache
from sms_engine.models import Backend
from typing import Dict, List


if hasattr(settings, 'TEST') and settings.TEST:
    CACHE_KEY = 'test:backend'
else:
    CACHE_KEY = 'backend'


def delete() -> None:
    key = CACHE_KEY
    dj_cache.delete(key)


def get(cache: bool = True) -> Dict[int, List[str]]:
    """ Get backend aliases as a dictionary which are cached by defaults.
    """
    key = CACHE_KEY
    backend_dict: Dict[int, List[str]] = {}

    if cache:
        # Hit cache first
        backend_aliases = dj_cache.get(key)
        if backend_aliases:
            return backend_aliases

    # Cache miss, build the dict
    backend_dict = {
        Backend.PRIORITY.high: [],
        Backend.PRIORITY.normal: [],
        Backend.PRIORITY.low: [],
    }
    backends = Backend.objects.filter(is_active=True).order_by('priority', 'id')
    for backend in backends:
        backend_dict[backend.priority].append(backend.alias)

    if cache:
        dj_cache.set(key, backend_dict)
    return backend_dict
