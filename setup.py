##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup

$Id:$
"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='z3c.jsonrpc',
    version='0.7.1dev',
    author = "Roger Ineichen and the Zope Community",
    author_email = "zope-dev@zope.org",
    description = "JSON RPC server and client implementation for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************'
        + '\n\n' +
        read('src', 'z3c', 'jsonrpc', 'README.txt')
        + '\n\n' +
        read('src', 'z3c', 'jsonrpc', 'zcml.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 z3c json rpc json-rpc server client",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/z3c.jsonrpc',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'z3c.coverage',
            'zope.app.testing',
            'zope.security',
            'zope.browserpage',
            'zope.principalregistry',
            'zope.testbrowser',
            'zope.testing',
            'zope.securitypolicy',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.json',
        'zope.app.publication',
        'zope.component',
        'zope.configuration',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.location',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.traversing',
        ],
    zip_safe = False,
)
