# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
    },
}


SMS_ENGINE = {
    'BACKENDS': {
        'default': 'sms_engine.backends.DummyBackend',
        'dummy': 'sms_engine.backends.DummyBackend',
        'always153': 'sms_engine.tests.backends.Always153Backend',
        'error': 'sms_engine.backends.RaiseExceptionBackend',
        'dynamic-test123': {
            'CLASS': 'sms_engine.tests.backends.DynamicBackend',
            'usr': 'test123',
            'pwd': 'test456',
        },
        'dynamic-proper-sender': {
            'CLASS': 'sms_engine.tests.backends.DynamicBackend',
            'usr': 'proper-sender',
            'pwd': 'proper-password',
        }
    },
}


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'sms_engine',
)

SMS_ENGINE_ROUTER = 'sms_engine.test_router.get_router'

SECRET_KEY = 'a'

ROOT_URLCONF = 'sms_engine.test_urls'

DEFAULT_FROM_EMAIL = 'webmaster@example.com'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

USE_TZ = True
TIME_ZONE = "Asia/Jakarta"
