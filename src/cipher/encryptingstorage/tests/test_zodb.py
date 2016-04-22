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
from zope.testing import setupstack

import base64
import cipher.encryptingstorage
import doctest
import os
import transaction
import unittest
import ZEO.tests.testZEO
import zlib
import ZODB.config
import ZODB.FileStorage
import ZODB.interfaces
import ZODB.MappingStorage
import ZODB.tests.StorageTestBase
import ZODB.tests.testFileStorage
import ZODB.utils
import zope.interface.verify


def test_config():
    r"""

To configure a encryptingstorage, import cipher.encryptingstorage and use the
encryptingstorage tag:

    >>> kek_key = base64.b64decode(
    ... '''LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpQcm9jLVR5cGU6IDQsRU5DUllQVEVECkRF
    ... Sy1JbmZvOiBERVMtRURFMy1DQkMsMTIwQkZGREQ3NEZGRjg0MQoKMFk1ODFGcHgyMzBIZjZRa3hP
    ... MVRvWjYvOU1YazhIK3pVUFNQemdTSXpnWWdJMUFwQTJMWEs5YlpudU1qbDNsUgpUUGpSWXBVWTFa
    ... ZHpYWmpvTGJRV2pYNzd6Z2JKQlc1T2RyWG9TSnNXKzAvWlRtWTUwNy8ycVIzbHVjK3VSTUtkCnRO
    ... OUtlandrbXArUno2TmhDM1ZDdHZqUktzaU5sRmgxYjhmTkQwUlRHcmFyQXZ5ZnpsZjdaVUlsUUVE
    ... ZGduNzIKOWkyTzRaNHo3aFlSdmc5aDlVSTMwc3FIaWk4c21taVlWTE9iaVF4clBQcXIzWkhXVDVK
    ... Rmt5VnQ2bnUyTFJaSwovWWpLSmY1dU9yU2VMdktNMDNiVUE3bGQrK1NMTElpK1c2RHYrbnNxWmRv
    ... ZkFocU0zMk9waTNRcHA2YUI4aEtlCnRSbytuYXhoNlMvTHNuT29kVXAwZ3kycE9tVVV5Q1RqM2JS
    ... YVRPcDhiVTY1aVhOY29scGlCVFdoRDcyVnM5VUEKZDNNWGtBbE5CUTdxQlFzUTJJODlWY2ZIOGFY
    ... YlZkUXQ2Y2ozWU1CWGU1ZDVIZGFUOGkvbzdzWlFpZXZWakFGbAo4SHJUVWFIcmN4bHBON0lyOThR
    ... alJreHRVZWplOUk1OVg2LzAvbFptS1hyRDA5V1NmTmtDSjRvTnA0MFNycnRUCi92MWh0cWVQc1lL
    ... MnkyekkvcWlCckJDZjg3YldFTXBseERTcC9lOFA1ZUwwSFgvMG9LQWNXc0VYUktPRWY4U3cKOXQv
    ... aXFnTjNJQ2tabEFFbG9wb2hOMUU4OVRkeEoza1JrMFFOU21XRU9QWUJXMTJQRDlhdnZlaU9CN2hT
    ... ODB5TAp1MjBJckhJVW82bkx0K1BwSHBwb0JSUFJvc2wzRTkwcG9LVDgvZnZLV2VwZmRLQTQwVmY5
    ... TVNvSFZOWDhMOFlXClpjUUlCbVZkcDMrZ0JLeGVwdlVWbStCcS9nSmpISUVROFlJL1ROYUltSGdJ
    ... aUE3YjEvS3pxRkNPcmZnS0pnY1kKbVR3NjdPWU44bnJFOE1XZnJMK0hVOW1HNkhYK09QY29GSFgw
    ... Y3FPNGxFYWZuY3JFRG14UUludVRaUDNvaER1Zwpac1dTZE8yd1Q0NXJEWmxUTGhneTR3aWpxUG1J
    ... TEwrU0RNemQ3R0h3cE0xcXJCNWU1UFo1dEpaRlc1cnlZSmdlClkyaFNIa1YxZWFGMWRBRTFWdUhv
    ... Qjd4d0hhckRXRkU4OFdsK1NwK0VETEZXSThzNGhteG5lTFdwOUFlMmc0WW0KbXNXalF3cXVtM0Nm
    ... dkw4eFJyWldqZDQvUTUxM2RtY1EvamRqeEhLWWFjMjJqdTBhRUljWG9qMzRoUnZYUTRDVwpBdlVF
    ... UnJjbDRUTmNDNkdSWFdvb3pQMFdDU0Jid3ZpRDJBVzdmWkpFK1BPSyt4d3ZhYUFSSXFsR2Urb3N5
    ... WDVOCmwrUWJyN2M0OGdmZExoNjlqT3UwS3JWaCs1ZUV6WUxYYTJnaHo2NHFheXh4cUY0R0F4ZmZQ
    ... WUt3cEl1eVRmdDEKZFd4bnNjVkM4QlZsM1N4V01tVnZ1SWNHR3ZjUUttUHQ3d2dxL3R0UWVCWlFK
    ... b1ZvQkhJK0l2QXNlQytsbC84RApvOU02bVJuT0VvckhIMWR5TGY5KzE1WkxkSFQzRU5oR2dTcitI
    ... ajI2Nm5ybWtXOG5jRFBVMDFKaTJNNE54TDJICi9mR0xwOTJOUllVc0xONytlQlFMZEY3T0g1VWhX
    ... N1BjMkRtMkFlSlZNSzFqRFEyR2plckJlK0tuUElQaVAwVE4KRG1WTUpSTmdMNkgzYlFBQVlzQUpU
    ... VlZGUEx5eTZxZHcrVDU0cXU3Uko3Qkk3SEtIRVlKc3E4WmxLcVhMRmhZLwpreW5mVjNNcE1LSGpi
    ... N0h0eHFKSzVNZ0tsN0ZST2VNazMyYVhhOGVJL0U3K0I1aXR6TWdranlSWFhJUFE5NkpHCkNxVVVC
    ... MDFKSERobERhUVBOTUpUTGpMOFpIMW5JWktHcGRIQWpFTXU5dGV2NUpYbjdYc1MrTW1pUDNXMUxm
    ... ZisKVmhQbmZaOGYvVms2eUhrVTBYN3dyK0duMERWZmtJamd0RWVuVE1RSUg4by91NTJjYzBUYTVn
    ... PT0KLS0tLS1FTkQgUlNBIFBSSVZBVEUgS0VZLS0tLS0='''
    ... )
    >>> with open('kek.key', 'w') as fp:
    ...     fp.write(kek_key)

    >>> os.makedirs('dek-storage/')
    >>> dek_key = base64.b64decode(
    ... '''esfiaDYeNFs1e2YDB7SVhSZnPmlSjWhlun21GWLGi4FGQxlWeXI37igz8R/tpC98Ca2MBBFjTIyJ
    ... kgWdR6GIR/hrT72EQjdY2TPCmLPuHpsxMkrvPyI+GqhNCKkk5UI4iafTnii4TDlxr3YXtjkES7oT
    ... VlxlviRUfsFSqIp+e0BsZqp53JTaWOFFlAi+dovYwk9UUE7OS8oujtBuHGjSlbYKWhtXNTt11vB2
    ... T7WKuFUjqvzju35sW0RuJSc94Quc53Gflxn8UdS8TDzQ1hBSjT3Kz9SIQupMvP9IENfOCy5OxSvT
    ... sv+x88MVb0i32weBUKx4E1KWOEsqf0/CoskrNg=='''
    ... )
    >>> with open('dek-storage/d9ac2bd4d6bacd56a9a288cdda05f102.dek', 'w') as fp:
    ...     fp.write(dek_key)

    >>> encryption_config = '''
    ... [encryptingstorage:encryption]
    ... enabled = true
    ... kek-path = kek.key
    ... dek-storage-path = dek-storage/
    ... '''
    >>> with open('encryption.conf', 'w') as fp:
    ...     fp.write(encryption_config)

    >>> config = '''
    ...     %import cipher.encryptingstorage
    ...     <zodb>
    ...         <encryptingstorage>
    ...             config encryption.conf
    ...             <filestorage>
    ...                 path data.fs
    ...                 blob-dir blobs
    ...             </filestorage>
    ...         </encryptingstorage>
    ...     </zodb>
    ... '''
    >>> db = ZODB.config.databaseFromString(config)

    >>> conn = db.open()
    >>> conn.root()['a'] = 1
    >>> transaction.commit()
    >>> conn.root()['b'] = ZODB.blob.Blob('Hi\nworld.\n')
    >>> transaction.commit()

    >>> db.close()

    >>> db = ZODB.config.databaseFromString(config)
    >>> conn = db.open()
    >>> conn.root()['a']
    1
    >>> conn.root()['b'].open().read()
    'Hi\nworld.\n'
    >>> db.close()

After putting some data in, the records will be encrypted:

    >>> for t in ZODB.FileStorage.FileIterator('data.fs'):
    ...     for r in t:
    ...         data = r.data
    ...         if r.data[:2] != '.e':
    ...             print 'oops', `r.oid`
    """

def test_config_no_encrypt():
    r"""

You can disable encryption.

    >>> config = '''
    ...     %import cipher.encryptingstorage
    ...     <zodb>
    ...         <encryptingstorage>
    ...             encrypt no
    ...             <filestorage>
    ...                 path data.fs
    ...                 blob-dir blobs
    ...             </filestorage>
    ...         </encryptingstorage>
    ...     </zodb>
    ... '''
    >>> db = ZODB.config.databaseFromString(config)

    >>> conn = db.open()
    >>> conn.root()['a'] = 1
    >>> transaction.commit()
    >>> conn.root()['b'] = ZODB.blob.Blob('Hi\nworld.\n')
    >>> transaction.commit()

    >>> db.close()

Since we didn't encrypt, we can open the storage using a plain file storage:

    >>> db = ZODB.DB(ZODB.FileStorage.FileStorage('data.fs', blob_dir='blobs'))
    >>> conn = db.open()
    >>> conn.root()['a']
    1
    >>> conn.root()['b'].open().read()
    'Hi\nworld.\n'
    >>> db.close()
    """

def test_config_fileconfig():
    r"""

You can pass the encryption options.

Create a sample config:

    >>> import tempfile
    >>> conf_path = tempfile.mktemp()
    >>> with open(conf_path, 'w') as f:
    ...     f.write('''
    ... [cipher:encryption]
    ... enabled = false
    ... ''')

Ditch the default utility:

    >>> from cipher.encryptingstorage import encrypt_util
    >>> encrypt_util.ENCRYPTION_UTILITY = None

Use the config tag to pass the filename:

    >>> config = '''
    ...     %import cipher.encryptingstorage
    ...     <zodb>
    ...         <encryptingstorage>
    ...             encrypt no
    ...             config __filename__
    ...             <filestorage>
    ...                 path data.fs
    ...                 blob-dir blobs
    ...             </filestorage>
    ...         </encryptingstorage>
    ...     </zodb>
    ... '''
    >>> config = config.replace('__filename__', conf_path)

    >>> db = ZODB.config.databaseFromString(config)

It's enough for now that the utility gets replaced:

    >>> encrypt_util.ENCRYPTION_UTILITY # doctest: +ELLIPSIS
    <cipher.encryptingstorage.encrypt_util.TrivialEncryptionUtility object at ...>

    """

def test_mixed_encrypted_and_unencrypted_and_packing():
    r"""
We can deal with a mixture of encrypted and unencrypted data.

First, we'll create an existing file storage:

    >>> db = ZODB.DB(ZODB.FileStorage.FileStorage('data.fs', blob_dir='blobs'))
    >>> conn = db.open()
    >>> conn.root.a = 1
    >>> transaction.commit()
    >>> conn.root.b = ZODB.blob.Blob('Hi\nworld.\n')
    >>> transaction.commit()
    >>> conn.root.c = conn.root().__class__((i,i) for i in range(100))
    >>> transaction.commit()
    >>> db.close()

Now let's open the database encrypted:

    >>> db = ZODB.DB(cipher.encryptingstorage.EncryptingStorage(
    ...     ZODB.FileStorage.FileStorage('data.fs', blob_dir='blobs')))
    >>> conn = db.open()
    >>> conn.root()['a']
    1
    >>> conn.root()['b'].open().read()
    'Hi\nworld.\n'
    >>> conn.root()['b'] = ZODB.blob.Blob('Hello\nworld.\n')
    >>> transaction.commit()
    >>> db.close()

Having updated the root, it is now encrypted.  To see this, we'll
open it as a file storage and inspect the record for object 0:

    >>> storage = ZODB.FileStorage.FileStorage('data.fs')
    >>> data, _ = storage.load('\0'*8)
    >>> data[:2] == '.e'
    True

Records that we didn't modify remain unencrypted

    >>> storage.load('\0'*7+'\2')[0] # doctest: +ELLIPSIS
    'cpersistent.mapping\nPersistentMapping...


    >>> storage.close()

Let's try packing the file 4 ways:

- using the encrypted storage:

    >>> open('data.fs.save', 'wb').write(open('data.fs', 'rb').read())
    >>> db = ZODB.DB(cipher.encryptingstorage.EncryptingStorage(
    ...     ZODB.FileStorage.FileStorage('data.fs', blob_dir='blobs')))
    >>> db.pack()
    >>> sorted(ZODB.utils.u64(i[0]) for i in record_iter(db.storage))
    [0, 2, 3]
    >>> db.close()

- using the storage in non-encrypt mode:

    >>> open('data.fs', 'wb').write(open('data.fs.save', 'rb').read())
    >>> db = ZODB.DB(cipher.encryptingstorage.EncryptingStorage(
    ...     ZODB.FileStorage.FileStorage('data.fs', blob_dir='blobs'),
    ...     encrypt=False))

    >>> db.pack()
    >>> sorted(ZODB.utils.u64(i[0]) for i in record_iter(db.storage))
    [0, 2, 3]
    >>> db.close()

- using the server storage:

    >>> open('data.fs', 'wb').write(open('data.fs.save', 'rb').read())
    >>> db = ZODB.DB(cipher.encryptingstorage.ServerEncryptingStorage(
    ...     ZODB.FileStorage.FileStorage('data.fs', blob_dir='blobs'),
    ...     encrypt=False))

    >>> db.pack()
    >>> sorted(ZODB.utils.u64(i[0]) for i in record_iter(db.storage))
    [0, 2, 3]
    >>> db.close()

- using the server storage in non-encrypted mode:

    >>> open('data.fs', 'wb').write(open('data.fs.save', 'rb').read())
    >>> db = ZODB.DB(cipher.encryptingstorage.ServerEncryptingStorage(
    ...     ZODB.FileStorage.FileStorage('data.fs', blob_dir='blobs'),
    ...     encrypt=False))

    >>> db.pack()
    >>> sorted(ZODB.utils.u64(i[0]) for i in record_iter(db.storage))
    [0, 2, 3]
    >>> db.close()
    """

class Dummy:

    def invalidateCache(self):
        print 'invalidateCache called'

    def invalidate(self, *args):
        print 'invalidate', args

    def references(self, record, oids=None):
        if oids is None:
            oids = []
        oids.extend(record.decode('hex').split())
        return oids

    def transform_record_data(self, data):
        return data.encode('hex')

    def untransform_record_data(self, data):
        return data.decode('hex')


def test_wrapping():
    r"""
Make sure the wrapping methods do what's expected.

    >>> s = cipher.encryptingstorage.EncryptingStorage(ZODB.MappingStorage.MappingStorage())
    >>> zope.interface.verify.verifyObject(ZODB.interfaces.IStorageWrapper, s)
    True

    >>> s.registerDB(Dummy())
    >>> s.invalidateCache()
    invalidateCache called

    >>> s.invalidate('1', range(3), '')
    invalidate ('1', [0, 1, 2], '')

    >>> data = ' '.join(map(str, range(9)))
    >>> transformed = s.transform_record_data(data)
    >>> transformed
    '.e.zx\x9c360206\x04b# 6\x06b\x13 6\x05b3 6\x07b\x0b\x00t,\x06\xb0'

    >>> s.untransform_record_data(transformed) == data
    True

    >>> s.references(transformed)
    ['0', '1', '2', '3', '4', '5', '6', '7', '8']

    >>> l = range(3)
    >>> s.references(transformed, l)
    [0, 1, 2, '0', '1', '2', '3', '4', '5', '6', '7', '8']

    >>> l
    [0, 1, 2, '0', '1', '2', '3', '4', '5', '6', '7', '8']

    """

def dont_double_encrypt():
    """
    This test is a bit artificial in that we want to make sure we
    don't double encrypt and we don't want to rely on not double
    encrypting simply because doing so would make the pickle smaller.
    So this test is actually testing that we don't encrypt strings
    that start with the encrypted marker.

    >>> data = '.e'+'x'*80
    >>> store = cipher.encryptingstorage.EncryptingStorage(ZODB.MappingStorage.MappingStorage())
    >>> store._transform(data) == data
    True
    """

def record_iter(store):
    next = None
    while 1:
        oid, tid, data, next = store.record_iternext(next)
        yield oid, tid, data
        if next is None:
            break


class FileStorageZlibTests(ZODB.tests.testFileStorage.FileStorageTests):

    def open(self, **kwargs):
        self._storage = cipher.encryptingstorage.EncryptingStorage(
            ZODB.FileStorage.FileStorage('FileStorageTests.fs',**kwargs))

class FileStorageZlibTestsWithBlobsEnabled(
    ZODB.tests.testFileStorage.FileStorageTests):

    def open(self, **kwargs):
        if 'blob_dir' not in kwargs:
            kwargs = kwargs.copy()
            kwargs['blob_dir'] = 'blobs'
        ZODB.tests.testFileStorage.FileStorageTests.open(self, **kwargs)
        self._storage = cipher.encryptingstorage.EncryptingStorage(self._storage)

class FileStorageZlibRecoveryTest(
    ZODB.tests.testFileStorage.FileStorageRecoveryTest):

    def setUp(self):
        ZODB.tests.StorageTestBase.StorageTestBase.setUp(self)
        self._storage = cipher.encryptingstorage.EncryptingStorage(
            ZODB.FileStorage.FileStorage("Source.fs", create=True))
        self._dst = cipher.encryptingstorage.EncryptingStorage(
            ZODB.FileStorage.FileStorage("Dest.fs", create=True))



class FileStorageZEOZlibTests(ZEO.tests.testZEO.FileStorageTests):
    _expected_interfaces = (
        ('ZODB.interfaces', 'IStorageRestoreable'),
        ('ZODB.interfaces', 'IStorageIteration'),
        ('ZODB.interfaces', 'IStorageUndoable'),
        ('ZODB.interfaces', 'IStorageCurrentRecordIteration'),
        ('ZODB.interfaces', 'IExternalGC'),
        ('ZODB.interfaces', 'IStorage'),
        ('ZODB.interfaces', 'IStorageWrapper'),
        ('zope.interface', 'Interface'),
        )

    def getConfig(self):
        return """\
        %import cipher.encryptingstorage
        <encryptingstorage>
        <filestorage 1>
        path Data.fs
        </filestorage>
        </encryptingstorage>
        """

class FileStorageClientZlibZEOZlibTests(FileStorageZEOZlibTests):

    def _wrap_client(self, client):
        return cipher.encryptingstorage.EncryptingStorage(client)

class FileStorageClientZlibZEOServerZlibTests(
    FileStorageClientZlibZEOZlibTests
    ):

    def getConfig(self):
        return """\
        %import cipher.encryptingstorage
        <serverencryptingstorage>
        <filestorage 1>
        path Data.fs
        </filestorage>
        </serverencryptingstorage>
        """

def test_suite():
    suite = unittest.TestSuite()
    for class_ in (
        FileStorageZlibTests,
        FileStorageZlibTestsWithBlobsEnabled,
        FileStorageZlibRecoveryTest,
        FileStorageZEOZlibTests,
        FileStorageClientZlibZEOZlibTests,
        FileStorageClientZlibZEOServerZlibTests,
        ):
        s = unittest.makeSuite(class_, "check")
        s.layer = ZODB.tests.util.MininalTestLayer(
            'encryptingstoragetests.%s' % class_.__name__)
        suite.addTest(s)

    suite.addTest(doctest.DocTestSuite(
        setUp=setupstack.setUpDirectory, tearDown=setupstack.tearDown
        ))
    return suite
