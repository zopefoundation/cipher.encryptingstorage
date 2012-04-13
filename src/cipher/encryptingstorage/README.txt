=============================================================
ZODB storage wrapper for encryption of database records
=============================================================

Idea and quite a lot of code taken from zc.zlibstorage.

The ``cipher.encryptingstorage`` package provides ZODB storage wrapper
implementations that provides encryption and compression of database records.

.. contents::

Usage
=====

The primary storage is ``cipher.encryptingstorage.EncryptingStorage``.
It is used as a wrapper around a lower-level storage.  From Python, it is
constructed by passing another storage, as in::

    import ZODB.FileStorage, cipher.encryptingstorage

    storage = cipher.encryptingstorage.EncryptingStorage(
        ZODB.FileStorage.FileStorage('data.fs'))

.. -> src

    >>> exec src
    >>> data = 'x' * 100
    >>> storage.transform_record_data(data).startswith('.e')
    True
    >>> storage.close()

When using a ZODB configuration file, the encryptingstorage tag is used::

    %import cipher.encryptingstorage

    <zodb>
      <encryptingstorage>
        <filestorage>
          path data.fs
        </filestorage>
      </encryptingstorage>
    </zodb>

.. -> src

    >>> import ZODB.config
    >>> db = ZODB.config.databaseFromString(src)
    >>> db.storage.transform_record_data(data).startswith('.e')
    True
    >>> db.close()

Note the ``%import`` used to load the definition of the
``encryptingstorage`` tag.

Use with ZEO
============

When used with a ZEO ClientStorage, you'll need to use a server encrypting
storage on the storage server.  This is necessary so that server
operations that need to get at unencrypted record data can do so.
This is accomplished using the ``serverencryptingstorage`` tag in your ZEO
server configuration file::

    %import cipher.encryptingstorage

    <zeo>
      address 8100
    </zeo>

    <serverencryptingstorage>
      <filestorage>
        path data.fs
      </filestorage>
    </serverencryptingstorage>

.. -> src

    >>> src = src[:src.find('<zeo>')]+src[src.find('</zeo>')+7:]

    >>> storage = ZODB.config.storageFromString(src)
    >>> storage.transform_record_data(data).startswith('.e')
    True
    >>> storage.__class__.__name__
    'ServerEncryptingStorage'

    >>> storage.close()

Applying encryption (and compression) on the client this way is attractive
because, in addition to reducing the size of stored database records on the
server, you also reduce the size of records sent from the server to the
client and the size of records stored in the client's ZEO cache.

Decrypting only
==================

By default, records are encrypted when written to the storage and
decrypted when read from the storage.  An ``encrypt`` option can be
used to disable encryption of records but still decrypt encrypted
records if they are encountered. Here's an example from in Python::

    import ZODB.FileStorage, cipher.encryptingstorage

    storage = cipher.encryptingstorage.EncryptingStorage(
        ZODB.FileStorage.FileStorage('data.fs'),
        encrypt=False)

.. -> src

    >>> exec src
    >>> storage.transform_record_data(data) == data
    True
    >>> storage.close()

and using the configurationb syntax::

    %import cipher.encryptingstorage

    <zodb>
      <encryptingstorage>
        encrypt false
        <filestorage>
          path data.fs
        </filestorage>
      </encryptingstorage>
    </zodb>

.. -> src

    >>> db = ZODB.config.databaseFromString(src)
    >>> db.storage.transform_record_data(data) == data
    True
    >>> db.close()

This option is useful when deploying the storage when there are
multiple clients.  If you don't want to update all of the clients at
once, you can gradually update all of the clients with a encryptingstorage
that doesn't do encryption, but recognizes encrypted records.  Then,
in a second phase, you can update the clients to encrypt records, at
which point, all of the clients will be able to read the encrypted
records produced.

Encrypting entire databases
============================

One way to encrypt all of the records in a database is to copy data
from an decrypted database to a encrypted one, as in::

    import ZODB.FileStorage, cipher.encryptingstorage

    orig = ZODB.FileStorage.FileStorage('data.fs')
    new = cipher.encryptingstorage.EncryptingStorage(
        ZODB.FileStorage.FileStorage('data.fs-copy'))
    new.copyTransactionsFrom(orig)

    orig.close()
    new.close()

.. -> src

    >>> conn = ZODB.connection('data.fs', create=True)
    >>> conn.root.a = conn.root().__class__([(i,i) for i in range(1000)])
    >>> conn.root.b = conn.root().__class__([(i,i) for i in range(2000)])
    >>> import transaction
    >>> transaction.commit()
    >>> conn.close()

    >>> exec(src)

    >>> new = cipher.encryptingstorage.EncryptingStorage(
    ...     ZODB.FileStorage.FileStorage('data.fs-copy'))
    >>> conn = ZODB.connection(new)
    >>> dict(conn.root.a) == dict([(i,i) for i in range(1000)])
    True
    >>> dict(conn.root.b) == dict([(i,i) for i in range(2000)])
    True

    >>> import ZODB.utils
    >>> for i in range(3):
    ...     if not new.base.load(ZODB.utils.p64(i))[0][:2] == '.e':
    ...         print 'oops', i
    >>> len(new)
    3

    >>> conn.close()

Record prefix
=============

Encrypted records have a prefix of ".e".  This allows a database to
have a mix of encrypted and not encrypted records.

Stand-alone encryption and decryption functions
===================================================

In anticipation of wanting to plug the encryption and decryption
logic into other tools without creating storages, the functions used
to decrypt and decrypt data records are available as
``cipher.encryptingstorage`` module-level functions:

``encrypt(data)``
  Encrypt the given data if:

    - it doesn't start with the encrypted-record marker, ``'.e'``

  The encrypted data are returned.

``decrypt(data)``
  Decrypt the data if it is encrypted.

  The decrypted (or original) data are returned.

.. basic sanity check :)

    >>> _ = (cipher.encryptingstorage.compress, cipher.encryptingstorage.decompress)

    >>> _ = (cipher.encryptingstorage.encrypt, cipher.encryptingstorage.decrypt)
