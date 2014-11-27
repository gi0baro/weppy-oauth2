# -*- coding: utf-8 -*-
"""
weppy-Oauth2
------------

This extension provides a simple interface to add oauth2 login in weppy.
"""

from setuptools import setup

setup(
    name='weppy-Oauth2',
    version='0.1',
    url='https://github.com/gi0baro/weppy-oauth2',
    license='BSD',
    author='Giovanni Barillari',
    author_email='gi0baro@d4net.org',
    description='Oauth2 login interface for weppy',
    long_description=__doc__,
    packages=['weppy_oauth2'],
    install_requires=['weppy'],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
