from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .compat import import_attribute, string_types


def get_backend(alias=None):
    """
    Return SMS Engine's backend instance
    """
    backend_config = get_available_backends()[alias or 'default']

    if isinstance(backend_config, string_types):
        return import_attribute(backend_config)()
    elif isinstance(backend_config, dict):
        # We have kwargs to be passed to the __init__ of the backend
        backend_class = backend_config.get("CLASS")
        if not backend_class:
            raise ImproperlyConfigured("%s backend is misconfigured!" % alias)
        return import_attribute(backend_class)(**backend_config)

    raise ImproperlyConfigured("Django Sms engine's backend is misconfigured!")


def get_available_backends():
    """ Get BACKENDS from sms_engine config
        There must be at least one backend
        and at least one of the backends is called `default` !
        Empty backend should not be allowed
    """
    backends = get_config().get('BACKENDS')

    if not backends or not backends.get('default'):
        raise ImproperlyConfigured('default backend is required')

    return backends


def get_config():
    """
    Returns SMS Engines's configuration in dictionary format. e.g:
    SMS_ENGINE = {
        'BACKENDS': {
            'twilio': sms_engine.backends.TwilioBackend
        }
    }
    """
    return getattr(settings, 'SMS_ENGINE', {})


def get_default_priority():
    return get_config().get('DEFAULT_PRIORITY', 'medium')


def get_log_level():
    return get_config().get('LOG_LEVEL', 1)
