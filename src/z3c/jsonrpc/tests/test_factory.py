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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import unittest

import zope.interface
import zope.component
from zope.component.testing import PlacelessSetup

from zope.app.publication.httpfactory import HTTPPublicationRequestFactory

from z3c.jsonrpc.publication import JSONRPCFactory
from z3c.jsonrpc.publication import JSONRPCPublication
from z3c.jsonrpc import interfaces


class DummyRequestFactory(object):
    def __call__(self, input_stream, env):
        self.input_stream = input_stream
        self.env = env
        return self

    def setPublication(self, pub):
        self.pub = pub


class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        self.__factory = HTTPPublicationRequestFactory(None)
        self.__env =  {
            'SERVER_URL':         'http://127.0.0.1',
            'HTTP_HOST':          '127.0.0.1',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0'
            }

    def test_jsonrpcfactory(self):
        jsonrpcrequestfactory = DummyRequestFactory()
        zope.interface.directlyProvides(
            jsonrpcrequestfactory, interfaces.IJSONRPCRequestFactory)
        zope.component.provideUtility(jsonrpcrequestfactory)
        env = self.__env
        factory = JSONRPCFactory()
        self.assertEqual(factory.canHandle(env), True)
        request, publication = factory()
        self.assertEqual(isinstance(request, DummyRequestFactory), True)
        self.assertEqual(publication, JSONRPCPublication)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))


if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
