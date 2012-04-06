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
import zlib
import ZODB.interfaces
import zope.interface

from cipher.encryptingstorage import encrypt_util

class EncryptingStorage(object):

    zope.interface.implements(ZODB.interfaces.IStorageWrapper)

    copied_methods = (
            'close', 'getName', 'getSize', 'history', 'isReadOnly',
            'lastTransaction', 'new_oid', 'sortKey',
            'tpc_abort', 'tpc_begin', 'tpc_finish', 'tpc_vote',
            'loadBlob', 'openCommittedBlobFile', 'temporaryDirectory',
            'supportsUndo', 'undo', 'undoLog', 'undoInfo',
            )

    def __init__(self, base, *args, **kw):
        self.base = base

        if (lambda encrypt=True: encrypt)(*args, **kw):
            self._transform = encrypt  # Refering to module func below!
        else:
            self._transform = lambda data: data

        self._untransform = decrypt

        for name in self.copied_methods:
            v = getattr(base, name, None)
            if v is not None:
                setattr(self, name, v)

        zope.interface.directlyProvides(self, zope.interface.providedBy(base))

        base.registerDB(self)

    def __getattr__(self, name):
        return getattr(self.base, name)

    def __len__(self):
        return len(self.base)

    def load(self, oid, version=''):
        data, serial = self.base.load(oid, version)
        return self._untransform(data), serial

    def loadBefore(self, oid, tid):
        r = self.base.loadBefore(oid, tid)
        if r is not None:
            data, serial, after = r
            return self._untransform(data), serial, after
        else:
            return r

    def loadSerial(self, oid, serial):
        return self._untransform(self.base.loadSerial(oid, serial))

    def pack(self, pack_time, referencesf, gc=None):
        _untransform = self._untransform
        def refs(p, oids=None):
            return referencesf(_untransform(p), oids)
        if gc is not None:
            return self.base.pack(pack_time, refs, gc)
        else:
            return self.base.pack(pack_time, refs)

    def registerDB(self, db):
        self.db = db
        self._db_transform = db.transform_record_data
        self._db_untransform = db.untransform_record_data

    _db_transform = _db_untransform = lambda self, data: data

    def store(self, oid, serial, data, version, transaction):
        return self.base.store(oid, serial, self._transform(data), version,
                               transaction)

    def restore(self, oid, serial, data, version, prev_txn, transaction):
        return self.base.restore(
            oid, serial, self._transform(data), version, prev_txn, transaction)

    def iterator(self, start=None, stop=None):
        for t in self.base.iterator(start, stop):
            yield Transaction(t)

    def storeBlob(self, oid, oldserial, data, blobfilename, version,
                  transaction):
        return self.base.storeBlob(
            oid, oldserial, self._transform(data), blobfilename, version,
            transaction)

    def restoreBlob(self, oid, serial, data, blobfilename, prev_txn,
                    transaction):
        return self.base.restoreBlob(oid, serial, self._transform(data),
                                     blobfilename, prev_txn, transaction)

    def invalidateCache(self):
        return self.db.invalidateCache()

    def invalidate(self, transaction_id, oids, version=''):
        return self.db.invalidate(transaction_id, oids, version)

    def references(self, record, oids=None):
        return self.db.references(self._untransform(record), oids)

    def transform_record_data(self, data):
        return self._transform(self._db_transform(data))

    def untransform_record_data(self, data):
        return self._db_untransform(self._untransform(data))

    def record_iternext(self, next=None):
        oid, tid, data, next = self.base.record_iternext(next)
        return oid, tid, self._untransform(data), next

    def copyTransactionsFrom(self, other):
        ZODB.blob.copyTransactionsFromTo(other, self)

    def copyTransactionsFrom(self, other):
        ZODB.blob.copyTransactionsFromTo(other, self)


def compress(data):
    if data and (len(data) > 20) and data[:2] != '.z':
        compressed = '.z'+zlib.compress(data)
        if len(compressed) < len(data):
            return compressed
    return data

def decompress(data):
    return data[:2] == '.z' and zlib.decompress(data[2:]) or data

def encrypt(data):
    try:
        if data[:2] == '.e':
            return data
    except TypeError:
        # a ZODB test passes None as data, be forgiving about that
        return data

    # 1. compress
    data = compress(data)

    # 2. encrypt here!!!
    data = encrypt_util.ENCRYPTION_UTILITY.encryptBytes(data)
    return '.e'+data

def decrypt(data):
    try:
        if data[:2] != '.e':
            # not an encrypted record, return as is
            return data
    except TypeError:
        return data
    # 1. decrypt here!!!
    data = encrypt_util.ENCRYPTION_UTILITY.decryptBytes(data[2:])
    # 2. decompress
    data = decompress(data)
    return data

class ServerEncryptingStorage(EncryptingStorage):
    """Use on ZEO storage server when EncryptingStorage is used on client

    Don't do conversion as part of load/store, but provide
    pickle decoding.
    """

    copied_methods = EncryptingStorage.copied_methods + (
        'load', 'loadBefore', 'loadSerial', 'store', 'restore',
        'iterator', 'storeBlob', 'restoreBlob', 'record_iternext',
        )

class Transaction(object):

    def __init__(self, trans):
        self.__trans = trans

    def __iter__(self):
        for r in self.__trans:
            if r.data:
                r.data = decrypt(r.data)
            yield r

    def __getattr__(self, name):
        return getattr(self.__trans, name)


class ZConfig:

    _factory = EncryptingStorage

    def __init__(self, config):
        self.config = config
        self.name = config.getSectionName()

    def open(self):
        base = self.config.base.open()
        encrypt = self.config.encrypt
        if encrypt is None:
            encrypt = True
        cfg = self.config.config
        if cfg is not None:
            # XXX: how to figure `here`?
            encrypt_util.init_local_facility(
                {'__file__': cfg, 'here': '.'})
        return self._factory(base, encrypt)

class ZConfigServer(ZConfig):

    _factory = ServerEncryptingStorage
