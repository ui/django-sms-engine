# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name='django-sms-engine',
    version='v0.0.1',
    author='PT Stampindo Lancar Jaya',
    author_email='selwin@stamps.co.id',
    packages=['sms_engine'],
    url='https://github.com/ui/django-sms-engine',
    license='MIT',
    description='A Django app to monitor and send sms asynchronously',
    long_description=open('README.rst').read(),
    zip_safe=False,
    include_package_data=True,
    package_data={'': ['README.rst']},
    install_requires=['django>=1.8', 'requests', 'twilio==3.6.6'],
    classifiers=[
        'Development Status :: 1 - Beta/Unstable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
