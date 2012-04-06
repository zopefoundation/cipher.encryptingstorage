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

import doctest
import transaction
import unittest
import cipher.encryptingstorage
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

    >>> config = '''
    ...     %import cipher.encryptingstorage
    ...     <zodb>
    ...         <encryptingstorage>
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
