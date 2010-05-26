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

import StringIO
import doctest
import persistent
import zope.interface
import zope.testing.cleanup
from zope.app.testing import functional

from z3c.json.interfaces import IJSONReader
from z3c.json.converter import JSONReader
from z3c.json.exceptions import ProtocolError
from z3c.json.proxy import JSONRPCProxy
from z3c.json.transport import Transport
from z3c.jsonrpc import layer
from z3c.jsonrpc.publication import JSONRPCPublication
from z3c.jsonrpc.publisher import JSONRPCRequest
from z3c.jsonrpc.publisher import MethodPublisher
from z3c.jsonrpc.publisher import JSON_RPC_VERSION


###############################################################################
#
# Test proxy
#
###############################################################################

class JSONRPCTestTransport(Transport):
    """Test transport that delegates to zope.app.testing.functional.HTTPCaller.

    It can be used like a normal transport, including support for basic 
    authentication.
    """

    verbose = False
    handleErrors = True

    def request(self, host, handler, request_body, verbose=0):
        request = "POST %s HTTP/1.0\n" % (handler,)
        request += "Content-Length: %i\n" % len(request_body)
        request += "Content-Type: application/json\n"

        host, extra_headers, x509 = self.get_host_info(host)
        if extra_headers:
            request += "Authorization: %s\n" % (
                dict(extra_headers)["Authorization"],)

        request += "\n" + request_body
        caller = HTTPCaller()
        response = caller(request, handle_errors=self.handleErrors)

        errcode = response.getStatus()
        errmsg = response.getStatusString()
        # This is not the same way that the normal transport deals with the
        # headers.
        headers = response.getHeaders()

        if errcode != 200:
            raise ProtocolError(host + handler, errcode, errmsg, headers)

        return self._parse_response(
            StringIO.StringIO(response.getBody()), sock=None)


def JSONRPCTestProxy(uri, transport=None, encoding=None, verbose=None,
    jsonId=None, handleErrors=True, jsonVersion=JSON_RPC_VERSION):
    """A factory that creates a server proxy using the ZopeJSONRPCTestTransport 
    by default."""
    if verbose is None:
        verbose = 0
    if transport is None:
        transport = JSONRPCTestTransport()
    if isinstance(transport, JSONRPCTestTransport):
        transport.handleErrors = handleErrors
    return JSONRPCProxy(uri, transport, encoding, verbose, jsonId, jsonVersion)


###############################################################################
#
# Test layer
#
###############################################################################

functional.defineLayer("JSONRPCTestingLayer", "ftesting.zcml")
 

###############################################################################
#
# Test component
#
###############################################################################

class IJSONRPCTestLayer(layer.IJSONRPCLayer):
    """JSON-RPC test layer interface used for zcml testing."""


class IJSONRPCTestSkin(IJSONRPCTestLayer):
    """The IJSONRPCTestSkin testing skin based on IJSONRPCLayer."""


class IA(zope.interface.Interface):
    """First content stub interface."""


class A(persistent.Persistent):
    """First content stub."""

    zope.interface.implements(IA)


class IB(zope.interface.Interface):
    """First content stub interface."""


class B(persistent.Persistent):
    """First content stub."""

    zope.interface.implements(IB)


class MethodsA(MethodPublisher):
    """Method publisher test class."""

    def hello(self):
        return "Hello A World"


class MethodsB(MethodPublisher):
    """Method publisher test class."""

    def hello(self):
        return "Hello B World"


class ForceResponseErrorJSONReader(JSONReader):
    """JSONReader wich only raise a ResponseError because of bad a bad string.
    """
    zope.interface.implements(IJSONReader)

    def read(self, aString, encoding=None):
        aBadString = u'{"id":"jsonrpc", "method":"hello", "no-params"}'
        return super(ForceResponseErrorJSONReader, self).read(aBadString, encoding)


class TestRequest(JSONRPCRequest):
    """modeled after zope.publisher.xmlrpc.TestRequest"""
    def __init__(self, body_instream=None, environ=None,
                 response=None, **kw):

        _testEnv =  {
            'SERVER_URL':         'http://127.0.0.1',
            'HTTP_HOST':          '127.0.0.1',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
            }

        if environ:
            _testEnv.update(environ)
        if kw:
            _testEnv.update(kw)
        if body_instream is None:
            body_instream = StringIO.StringIO('')

        super(TestRequest, self).__init__(
            body_instream, _testEnv, response)


class HTTPCaller(functional.HTTPCaller):
    """HTTPCaller for JSON."""

    def chooseRequestClass(self, method, path, environment):
        """Choose and return a request class and a publication class"""
        request_cls, publication_cls = \
            super(HTTPCaller, self).chooseRequestClass(method, path,
                environment)
        
        content_type = environment.get('CONTENT_TYPE', '')
        is_json = content_type.startswith('application/json')
    
        if method in ('GET', 'POST', 'HEAD'):
            if (method == 'POST' and is_json):
                request_cls = JSONRPCRequest
                publication_cls = JSONRPCPublication
    
        return request_cls, publication_cls


###############################################################################
#
# Doctest setup
#
###############################################################################
def _prepare_doctest_keywords(kw):
    globs = kw.setdefault('globs', {})
    globs['http'] = HTTPCaller()
    globs['getRootFolder'] = functional.getRootFolder
    globs['sync'] = functional.sync

    kwsetUp = kw.get('setUp')
    def setUp(test):
        functional.FunctionalTestSetup().setUp()
        if kwsetUp is not None:
            kwsetUp(test)
    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        if kwtearDown is not None:
            kwtearDown(test)
        functional.FunctionalTestSetup().tearDown()
    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old
                             | doctest.ELLIPSIS
                             | doctest.REPORT_NDIFF
                             | doctest.NORMALIZE_WHITESPACE)


def FunctionalDocFileSuite(*paths, **kw):
    # use our custom HTTPCaller and layer
    kw['package'] = doctest._normalize_module(kw.get('package'))
    _prepare_doctest_keywords(kw)
    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = JSONRPCTestingLayer
    return suite


###############################################################################
#
# Test helper, make us independent from zope.app.testing
#
###############################################################################

# Setup of test text files as modules
import sys

# Evil hack to make pickling work with classes defined in doc tests
class NoCopyDict(dict):
    def copy(self):
        return self

class FakeModule:
    """A fake module."""
    
    def __init__(self, dict):
        self.__dict = dict

    def __getattr__(self, name):
        try:
            return self.__dict[name]
        except KeyError:
            raise AttributeError(name)


def setUpTestAsModule(test, name=None):
    if name is None:
        if test.globs.haskey('__name__'):
            name = test.globs['__name__']
        else:
            name = test.globs.name

    test.globs['__name__'] = name 
    test.globs = NoCopyDict(test.globs)
    sys.modules[name] = FakeModule(test.globs)


def tearDownTestAsModule(test):
    del sys.modules[test.globs['__name__']]
    test.globs.clear()


###############################################################################
#
# Unittest setup
#
###############################################################################

def setUp(test):
    setUpTestAsModule(test, name='README')


def tearDown(test):
    # ensure that we cleanup everything
    zope.testing.cleanup.cleanUp()
    tearDownTestAsModule(test)
