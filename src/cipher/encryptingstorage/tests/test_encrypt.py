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
"""Python utility tests"""
import doctest
import os
import tempfile
import shutil

from keas.kmi import facility
from zope.app.testing import setup

from cipher.encryptingstorage import encrypt_util


def doctest_EncryptionUtility():
    r"""Encryption Utility

    First we set up an encryption utility using a local key management
    facility:

      >>> storage_dir = tempfile.mkdtemp()
      >>> kek_path = os.path.join(storage_dir, 'key.kek')
      >>> kmf = facility.KeyManagementFacility(storage_dir)
      >>> util = encrypt_util.EncryptionUtility(kek_path, kmf)

    Re-iniitalizing the utility will reuse the generated key:

      >>> util = encrypt_util.EncryptionUtility(kek_path, kmf)

    Encrypt text:

      >>> data = util.encrypt(u'test')
      >>> len(data)
      16

    Decrypt text:

      >>> util.decrypt(data)
      u'test'
      >>> util.decrypt('bad')
      u'bad'

      >>> shutil.rmtree(storage_dir)
    """

def doctest_init_local_facility():
    r"""Initialize Local Facility

    Encryption disabled:

      >>> conf_path = tempfile.mktemp()
      >>> with open(conf_path, 'w') as f:
      ...     f.write('''
      ... [encryptingstorage:encryption]
      ... enabled = false
      ... ''')

      >>> encrypt_util.init_local_facility({'__file__': conf_path})
      >>> encrypt_util.ENCRYPTION_UTILITY
      <cipher.encryptingstorage.encrypt_util.TrivialEncryptionUtility object at ...>

    Local Encryption:

      >>> storage_dir = tempfile.mkdtemp()
      >>> kek_path = tempfile.mktemp()

      >>> with open(conf_path, 'w') as f:
      ...     f.write('''
      ... [encryptingstorage:encryption]
      ... enabled = true
      ... kek-path = %s
      ... dek-storage-path = %s
      ... ''' %(kek_path, storage_dir))

      >>> encrypt_util.init_local_facility({'__file__': conf_path, 'here': '.'})
      >>> encrypt_util.ENCRYPTION_UTILITY
      <cipher.encryptingstorage.encrypt_util.EncryptionUtility object at ...>
      >>> encrypt_util.ENCRYPTION_UTILITY.facility
      <KeyManagementFacility (1)>

      >>> shutil.rmtree(storage_dir)
      >>> os.remove(kek_path)

    Remote Encryption:

      >>> storage_dir = tempfile.mkdtemp()
      >>> kek_path = tempfile.mktemp()

      >>> with open(conf_path, 'w') as f:
      ...     f.write('''
      ... [encryptingstorage:encryption]
      ... enabled = true
      ... kek-path = %s
      ... kmi-server = http://localhost:8001/
      ... ''' %kek_path)

      >>> encrypt_util.init_local_facility({'__file__': conf_path, 'here': '.'})
      >>> encrypt_util.ENCRYPTION_UTILITY
      <cipher.encryptingstorage.encrypt_util.EncryptionUtility object at ...>
      >>> encrypt_util.ENCRYPTION_UTILITY.facility
      <LocalKeyManagementFacility 'http://localhost:8001/'>

      >>> shutil.rmtree(storage_dir)
      >>> os.remove(kek_path)

      >>> os.remove(conf_path)
      """

def setUp(test):
    setup.placelessSetUp(test)
    test.generate = facility.LocalKeyManagementFacility.generate
    facility.LocalKeyManagementFacility.generate = lambda s: 'foo'

def tearDown(test):
    facility.LocalKeyManagementFacility.generate = test.generate
    encrypt_util.ENCRYPTION_UTILITY = encrypt_util.TrivialEncryptionUtility()
    setup.placelessTearDown()

def test_suite():
    return doctest.DocTestSuite(
        setUp=setUp, tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|
                    doctest.ELLIPSIS|
                    doctest.REPORT_ONLY_FIRST_FAILURE
                    #|doctest.REPORT_NDIFF
                    )
