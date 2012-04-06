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

import manuel.capture
import manuel.doctest
import manuel.testing
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(manuel.testing.TestSuite(
        manuel.doctest.Manuel() + manuel.capture.Manuel(),
        '../README.txt',
        setUp=setupstack.setUpDirectory, tearDown=setupstack.tearDown
        ))
    return suite
