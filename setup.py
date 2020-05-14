##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
"""Setup for package cipher.encryptingstorage
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='cipher.encryptingstorage',
    version='1.1.1.dev0',
    url="http://pypi.python.org/pypi/cipher.encryptingstorage/",
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    description="ZODB storage wrapper for encryption of database records",
    long_description=(
        read('README.rst')
        + '\n\n' +
        read('CHANGES.rst')
        ),
    license='ZPL 2.1',
    keywords='Python Zope encryption',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP'],
    packages=find_packages('src'),
    namespace_packages=['cipher'],
    package_dir={'': 'src'},
    install_requires=[
        'ZODB3 >=3.10.0b1',
        'setuptools',
        'keas.kmi >= 3.1.0',
        ],
    extras_require=dict(
        test=[
            'zope.testing',
            'zope.app.testing',
            'manuel',
            'mock <= 3.0.5;python_version == "2.7"']),
    include_package_data=True,
    zip_safe=False,
    )
