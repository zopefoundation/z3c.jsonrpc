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
from zope.security.proxy import isinstance

from z3c.json.interfaces import IJSONReader
from z3c.json.interfaces import IJSONWriter
from z3c.json.converter import premarshal
from z3c.jsonrpc import interfaces
from z3c.jsonrpc.interfaces import JSON_CHARSETS

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
    """JSON-RPC request implementation based on IHTTPRequest."""

    _jsonId = 'jsonrpc'
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
        data = json.read(input)
        if self.jsonId is None:
            self.jsonId = data.get('id', self._jsonId)
        params = data['params']

        if isinstance(params, list):
            # json-rpc 1.0
            args = params
            # now, look for keyword parameters, the old way
            kwargs = None
            notPositional = []
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
                                if type_name == 'list':
                                    d = [d]
                                if type_name == 'tuple':
                                    d = tuple(d)
                        self.form[key] = d
        elif isinstance(params, dict):
            # json-rpc 1.2
            # Note: the JSONRPCProxy uses allways a dict for params. This means
            # we only use this part for extract the data.

            # Get the numeric params for positional params
            # This was proposed for json-rpc 1.1 but seems not get accepted.
            # The new 2.0 proposal only defines named paramters if they get
            # applied as key/value pair.
            
            # review and check this implementation after JSON-RPC 2.0 final
            temp_positional = []
            for key in params:
                if str(key).isdigit():
                    temp_positional.append((key, params[key]))
            temp_positional.sort(key=intsort)
            args = []
            # make args from positional args and remove them from params
            for item in temp_positional:
                args.append(item[1])
                del params[item[0]]
            # drop remaining named params into request.form
            for named_param in params:
                # named_param is unicode; python needs string for param names
                self.form[str(named_param)] = params[named_param]
        else:
            raise TypeError, 'Unsupported type for JSON-RPC "params" (%s)' \
                % type(params)
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

    def __getitem__(self,key):
        return self.get(key)


class JSONRPCResponse(HTTPResponse):
    """JSON-RPC Response"""


    def setResult(self, result):
        """The result dict contains the following key value pairs

        id -- json request id
        result -- result or null on error
        error -- error or null if result is Ok

        """
        id = self._request.jsonId
        if id is not None:
            result = premarshal(result)
            wrapper = {'id': id}
            wrapper['result'] = result
            wrapper['error'] = None
            json = zope.component.getUtility(IJSONWriter)
            encoding = getCharsetUsingRequest(self._request)
            result = json.write(wrapper)
            body = self._prepareResult(result)
            super(JSONRPCResponse,self).setResult(body)
            logger.log(DEBUG, "%s" % result)
        else:
            self.setStatus(204)
            super(JSONRPCResponse,self).setResult('')

    def _prepareResult(self, result):
        # we've asked json to return unicode; result should be unicode
        encoding = getCharsetUsingRequest(self._request) or 'utf-8'
        enc = encoding.lower()
        if not enc in JSON_CHARSETS:
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
        t, value = exc_info[:2]
        exc_data = []
        for file, lineno, function, text in traceback.extract_tb(exc_info[2]):
            exc_data.append("%s %s %s %s %s" % (file, "line",
                lineno, "in", function))
            exc_data.append("%s %s" % ( "=>", repr(text)))
            exc_data.append( "** %s: %s" % exc_info[:2])
        logger.log(logging.ERROR, "\n".join(exc_data))
        s = '%s: %s' % (getattr(t, '__name__', t), value)
        wrapper = {'id': self._request.jsonId}
        wrapper['result'] = None
        wrapper['error'] = s
        json = zope.component.getUtility(IJSONWriter)
        result = json.write(wrapper)
        body = self._prepareResult(result)
        super(JSONRPCResponse, self).setResult(body)
        logger.log(DEBUG, "Exception: %s" % result)
        self.setStatus(200)
