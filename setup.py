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
    version='1.0.0',
    url="http://pypi.python.org/pypi/cipher.encryptingstorage/",
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    description="ZODB storage wrapper for encryption of database records",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license='ZPL 2.1',

    packages=find_packages('src'),
    namespace_packages=['cipher'],
    package_dir={'': 'src'},
    install_requires=[
        'ZODB3 >=3.10.0b1',
        'setuptools',
        'keas.kmi',
        ],
    extras_require=dict(
        test=[
            'zope.testing',
            'zope.app.testing',
            'manuel']),
    include_package_data=True,
    zip_safe=False,
    )
