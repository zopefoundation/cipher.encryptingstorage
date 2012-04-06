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

from __future__ import absolute_import
import ConfigParser
import os

import M2Crypto
import zope.component
import zope.interface
from keas.kmi import facility
from keas.kmi.interfaces import IKeyHolder


class IEncryptionUtility(zope.interface.Interface):

    def encrypt(data):
        """Returns the encrypted data"""

    def decrypt(data):
        """Returns the decrypted data"""

    def encryptBytes(data):
        """Returns the encrypted data uses str, without utf-8 conversion"""

    def decryptBytes(data):
        """Returns the decrypted data uses str, without utf-8 conversion"""


class TrivialEncryptionUtility(object):

    def encrypt(self, data):
        return self.encryptBytes(data.encode('utf-8'))

    def decrypt(self, data):
        return self.decryptBytes(data).decode('utf-8')

    def encryptBytes(self, data):
        return data

    def decryptBytes(self, data):
        return data


class EncryptionUtility(TrivialEncryptionUtility):
    zope.interface.implements(IEncryptionUtility, IKeyHolder)

    def __init__(self, kek_path, facility):
        self.facility = facility
        if os.path.exists(kek_path):
            with open(kek_path, 'rb') as file:
                self.key = file.read()
        else:
            self.key = self.facility.generate()
            with open(kek_path, 'wb') as file:
                file.write(self.key)

    def encryptBytes(self, data):
        return self.facility.encrypt(self.key, data)

    def decryptBytes(self, data):
        try:
            return self.facility.decrypt(self.key, data)
        except M2Crypto.EVP.EVPError:
            return data


ENCRYPTION_UTILITY = TrivialEncryptionUtility()


def init_local_facility(conf):
    config = ConfigParser.RawConfigParser()
    config.readfp(open(conf['__file__'], 'r'))

    global ENCRYPTION_UTILITY

    enabled = False
    if config.has_option('encryptingstorage:encryption', 'enabled'):
        enabled = config.getboolean('encryptingstorage:encryption', 'enabled')

    if enabled:
        kek_path = config.get('encryptingstorage:encryption', 'kek-path')

        if config.has_option('encryptingstorage:encryption', 'kmi-server'):
            kmf = facility.LocalKeyManagementFacility(
                config.get('encryptingstorage:encryption', 'kmi-server'))
        else:
            kmf = facility.KeyManagementFacility(
                config.get('encryptingstorage:encryption', 'dek-storage-path'))

        if kek_path.startswith('/'):
            path = kek_path
        else:
            path = os.path.join(conf['here'], kek_path)

        ENCRYPTION_UTILITY = EncryptionUtility(path, kmf)

        # encryptingstorage specific:
        # just don't provide utilities, who knows what will be defined
        # by the main app

        #provideUtility(ENCRYPTION_UTILITY, IKeyHolder)
        #provideUtility(kmf)

    else:
        ENCRYPTION_UTILITY = TrivialEncryptionUtility()
