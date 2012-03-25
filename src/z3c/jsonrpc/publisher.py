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

import re
import traceback
import logging

import zope.interface
import zope.component
from zope.location.location import Location
from zope.i18n.interfaces import IUserPreferredCharsets
from zope.publisher.http import HTTPRequest
from zope.publisher.http import HTTPResponse
from zope.publisher.http import getCharsetUsingRequest
from zope.publisher.http import DirectResult
from zope.security.proxy import isinstance

from z3c.json.interfaces import IJSONReader
from z3c.json.interfaces import IJSONWriter
from z3c.json.converter import premarshal
from z3c.jsonrpc import interfaces
from z3c.jsonrpc import exception

JSON_RPC_VERSION = '2.0'

DEBUG = logging.DEBUG
logger = logging.getLogger()


def intsort(item):
    return int(item[0])


class MethodPublisher(Location):
    """Base class for JSON-RPC views that publish methods
       like zope.app.publisher.xmlrpc.MethodPublisher
    """
    zope.interface.implements(interfaces.IMethodPublisher)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __getParent(self):
        return hasattr(self, '_parent') and self._parent or self.context

    def __setParent(self, parent):
        self._parent = parent

    __parent__ = property(__getParent, __setParent)


class MethodTraverser(object):
    zope.interface.implements(interfaces.IJSONRPCPublisher)

    __used_for__ = interfaces.IMethodPublisher

    def __init__(self, context, request):
        self.context = context

    def publishTraverse(self, request, name):
        return getattr(self.context, name)


class JSONRPCRequest(HTTPRequest):
    """JSON-RPC request implementation based on IHTTPRequest.
    
    This implementation supports the following JSON-RPC Specification versions:
    
    - 1.0
    - 1.1
    - 2.0
    
    Version 1.0 and 1.1 offers params as a list. This params get converted to
    positional arguments if calling the JSON-RPC function.
    
    The version 2.0 offers support for named key/value params. The important 
    thing to know is that this implementation will convert named params kwargs 
    to form paramters. This means the method doesn't get any key word argument. 
    The reason why I was choosing is the existing publisher implementation and 
    it's debugger integration. If someone likes to integrate **kwargs support, 
    take a look at the publisher.publish method and it's mapply function which 
    get wrapped by the Debugger class. I hope that's fine for now and I 
    recommend to avoid kwargs for JSON-RPC methods ;-)

    The z3c.jsonrpcclient JavaScript method JSONRPCProxy converts a 
    typeof object as arguments[0] to named key/value pair arguments.

    """

    _jsonId = 'jsonrpc'
    jsonVersion = JSON_RPC_VERSION
    jsonId = None

    zope.interface.implements(interfaces.IJSONRPCRequest,
        interfaces.IJSONRPCApplicationRequest)

    def __init__(self, body_instream, environ, response=None):
        self.form = {}
        self._args = ()
        self.charsets = None
        super(JSONRPCRequest, self).__init__(body_instream, environ, response)

    def _createResponse(self):
        """return a response"""
        return JSONRPCResponse()

    def _decode(self, text):
        """Try to decode the text using one of the available charsets."""
        if self.charsets is None:
            envadapter = IUserPreferredCharsets(self)
            self.charsets = envadapter.getPreferredCharsets() or ['utf-8']
        for charset in self.charsets:
            try:
                text = unicode(text, charset)
                break
            except UnicodeError:
                pass
        return text

    _typeFormat = re.compile('([a-zA-Z][a-zA-Z0-9_]+|\\.[xy])$')

    def processInputs(self):
        """take the converted request and make useful args of it."""
        json = zope.component.getUtility(IJSONReader)
        stream = self._body_instream
        input = []
        incoming = stream.read(1000)
        while incoming:
            input.append(incoming)
            incoming = stream.read(1000)
        input = ''.join(input)
        # ensure unicode
        if not isinstance(input, unicode):
            input = self._decode(input)
        try:
            data = json.read(input)
        except:
            # catch any error since we don't know which library is used as 
            # parser
            raise exception.ParseError
        # get the params
        params = data.get('params', [])
        if self.jsonId is None:
            self.jsonId = data.get('id', self._jsonId)

        # get the json version. The version 1.0 offers no version argument.
        # The version 1.1 offers a version key and since version 2.0 the 
        # version is given with the ``jsonrpc`` key. Let's try to find the 
        # version for our request.
        self.jsonVersion = data.get('version', self.jsonVersion)
        self.jsonVersion = data.get('jsonrpc', self.jsonVersion)
        if self.jsonVersion in ['1.0', '1.1', '2.0']:
            # json-rpc 1.0 and 1.1
            if isinstance(params, list):
                args = params
                # version 1.0 and 1.1 uses a list of arguments
                for arg in args:
                    if isinstance(arg, dict):
                        # set every dict key value as form items and support at 
                        # least ``:list`` and ``:tuple`` input field name postifx
                        # conversion.
                        for key, d in arg.items():
                            key = str(key)
                            pos = key.rfind(":")
                            if pos > 0:
                                match = self._typeFormat.match(key, pos + 1)
                                if match is not None:
                                    key, type_name = key[:pos], key[pos + 1:]
                                    if type_name == 'list' and not isinstance(d, list):
                                        d = [d]
                                    if type_name == 'tuple' and not isinstance(d, tuple):
                                        d = tuple(d)
                            self.form[key] = d
            elif isinstance(params, dict):
                # process the key/value pair params. This arguments get stored
                # in the request.form argument and we skip it from method calls.
                # This means this library will not support key word arguments
                # for method calls. It will instead store them in the form.
                # This has two reasons.
                # 1. Zope doesn't support kwargs in the publication 
                #    implementation. It only supports positional arguments
                # 2. The JSON-RPC specification doesn't allow to use positional
                #     and keyword arguments on one method call
                # 3. Python doesn't allow to convert kwargs to positional 
                #    arguments because a dict doesn't provide an order
                # This means you should avoid to call a method with kwargs.
                # just use positional arguments if possible. Or get them from
                # directly from the request or request.form argument in your
                # code. Let me know if this is a real problem for you and you
                # like to implement a different kwarg handling. We have some 
                # ideas for add support for this.
                args = params
                # set every dict key value as form items and support at 
                # least ``:list`` and ``:tuple`` input field name postifx
                # conversion.
                for key, d in args.items():
                    key = str(key)
                    pos = key.rfind(":")
                    if pos > 0:
                        match = self._typeFormat.match(key, pos + 1)
                        if match is not None:
                            key, type_name = key[:pos], key[pos + 1:]
                            if type_name == 'list' and not isinstance(d, list):
                                d = [d]
                            if type_name == 'tuple' and not isinstance(d, tuple):
                                d = tuple(d)
                    self.form[key] = d
                args = []
            elif params is None:
                args = []
        else:
            raise TypeError, 'Unsupported JSON-RPC version (%s)' % \
                self.jsonVersion
        self._args = tuple(args)
        # make environment, cookies, etc., available to request.get()
        super(JSONRPCRequest,self).processInputs()
        self._environ['JSONRPC_MODE'] = True

        # split here on '.' for get path suffix steps
        functionstr = data['method']
        function = functionstr.split('.')
        if function:
            # translate '.' to '/' in function to represent object traversal.
            self.setPathSuffix(function)

    def traverse(self, object):
        return super(JSONRPCRequest, self).traverse(object)

    def keys(self):
        """See Interface.Common.Mapping.IEnumerableMapping."""
        d = {}
        d.update(self._environ)
        d.update(self._cookies)
        d.update(self.form)
        return d.keys()

    def get(self, key, default=None):
        """See Interface.Common.Mapping.IReadMapping."""
        marker = object()
        result = self.form.get(key, marker)
        if result is not marker:
            return result
        return super(JSONRPCRequest, self).get(key, default)

    def __getitem__(self, key):
        return self.get(key)


class JSONRPCResponse(HTTPResponse):
    """JSON-RPC Response"""

    def setResult(self, result):
        """The result dict contains the following key value pairs

        The version 1.0 and 1.1 provides a response dict with the following 
        arguments:

        id -- json request id
        result -- result or null on error
        error -- error or null if result is Ok

        The version 2.0 provides a response dict with the following named 
        paramters:

        jsonrpc -- jsonrpc version 2.0 or higher in future versions
        id -- json request id
        result -- result if no error is raised
        error -- error if any given

        """
        jsonId = self._request.jsonId
        jsonVersion = self._request.jsonVersion

        if interfaces.IJSONRPCErrorView.providedBy(result):
            if self._request.jsonVersion == "1.0":
                wrapper = {'result': None,
                           'error': result.message,
                           'id': self._request.jsonId}
            elif self._request.jsonVersion == "1.1":
                wrapper = {'version': self._request.jsonVersion,
                           'error': result.message,
                           'id': self._request.jsonId}
            else:
                wrapper = {'jsonrpc': self._request.jsonVersion,
                           'error': {'code': result.code,
                                     'message': result.message,
                                     'data': result.data},
                           'id': self._request.jsonId}
    
            try:
                json = zope.component.getUtility(IJSONWriter)
                result = json.write(wrapper)
                body = self._prepareResult(result)
                super(JSONRPCResponse, self).setResult(DirectResult((body,)))
                logger.log(DEBUG, "Exception: %s" % result)
                # error response is not really an error, it's valid response
                self.setStatus(200)
            except:
                # Catch all exceptions at this point
                self.handleException(sys.exc_info())
                return

        else:
            result = premarshal(result)
            if jsonVersion == "1.0":
                wrapper = {'result': result, 'error': None, 'id': jsonId}
            elif jsonVersion == "1.1":
                wrapper = {'version': jsonVersion, 'result': result, 'id': jsonId}
            else:
                wrapper = {'jsonrpc': jsonVersion, 'result': result, 'id': jsonId}
            json = zope.component.getUtility(IJSONWriter)
            encoding = getCharsetUsingRequest(self._request)
            result = json.write(wrapper)
            body = self._prepareResult(result)
            super(JSONRPCResponse,self).setResult(DirectResult((body,)))
            logger.log(DEBUG, "%s" % result)

    def _prepareResult(self, result):
        # we've asked json to return unicode; result should be unicode
        encoding = getCharsetUsingRequest(self._request) or 'utf-8'
        enc = encoding.lower()
        if not enc in interfaces.JSON_CHARSETS:
            encoding = 'utf-8'
        # encode outgoing boundary.
        if isinstance(result, unicode):
            body = result.encode(encoding)
            charset = encoding
        else:
            # something's wrong. JSON did not return unicode.
            raise TypeError, "JSON did not return unicode (%s)" % type(result)

        # set content type
        self.setHeader('content-type', "application/x-javascript;charset=%s" \
            % charset)
        return body

    def handleException(self, exc_info):
        # only legacy Exception where we didn't define a view for get handled
        # by this method. All exceptions where we have a view registered for
        # get handled by the setResult method based on the given
        # IJSONRPCErrorView
        t, value = exc_info[:2]
        exc_data = []
        for file, lineno, function, text in traceback.extract_tb(exc_info[2]):
            exc_data.append("%s %s %s %s %s" % (file, "line",
                lineno, "in", function))
            exc_data.append("%s %s" % ( "=>", repr(text)))
            exc_data.append( "** %s: %s" % exc_info[:2])
        logger.log(logging.ERROR, "\n".join(exc_data))
        s = '%s: %s' % (getattr(t, '__name__', t), value)
        if self._request.jsonVersion == "1.0":
            wrapper = {'result': None,
                       'error': s,
                       'id': self._request.jsonId}
        elif self._request.jsonVersion == "1.1":
            wrapper = {'version': self._request.jsonVersion,
                       'error': s,
                       'id': self._request.jsonId}
        else:
            # this only happens if error handling was running into en error or
            # if we didn't define an IJSONRPCErrorView for a given error
            wrapper = {'jsonrpc': self._request.jsonVersion,
                       'error': {'code': -32603,
                                 'message': 'Internal error',
                                 'data': s},
                       'id': self._request.jsonId}

        json = zope.component.getUtility(IJSONWriter)
        result = json.write(wrapper)
        body = self._prepareResult(result)
        super(JSONRPCResponse, self).setResult(DirectResult((body,)))
        logger.log(DEBUG, "Exception: %s" % result)
        self.setStatus(200)
