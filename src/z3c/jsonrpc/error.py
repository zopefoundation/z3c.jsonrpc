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

import zope.i18n
import zope.i18nmessageid

_ = zope.i18nmessageid.MessageFactory('z3c')

from z3c.jsonrpc import interfaces

# The error codes used since JSON-RPC 2.0
# See: http://groups.google.com/group/json-rpc/web/json-rpc-1-2-proposal
#
# code   message           Meaning 
# --------------------------------
# -32700 Parse error.          Invalid JSON. An error occurred on the server 
#                              while parsing the JSON text.
# -32600 Invalid Request.      The received JSON not a valid JSON-RPC Request.
# -32601 Method not found.     The requested remote-procedure does not exist, 
#                              is not available.
# -32602 Invalid params.       Invalid method parameters.
# -32603 Internal error.       Internal JSON-RPC error.
# -32099..-32000 Server error. Reserved for implementation-defined server-errors.


class JSONRPCErrorView(object):
    """Generic JSON-RPC error view.
    
    This base class is used for error views which are used for error handling
    by ZopePublication.
    """
    
    zope.interface.implements(interfaces.IJSONRPCErrorView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """Must return itself.
        
        This allows us to use the error view in setResult if ZopePublication
        is adapting an error view to error and request and calls them.
        """
        return self


class ParseErrorView(JSONRPCErrorView):
    """Knows the error data for parse errors."""

    code = -32700
    message = u'Parse error'

    @property
    def data(self):
        errMsg = _('Parse error')
        return {'i18nMessage':zope.i18n.translate(errMsg, context=self.request)}


class InvalidRequestErrorView(JSONRPCErrorView):
    """Knows the error data for invalid request errors."""

    code = -32600
    message = u'Invalid Request'

    @property
    def data(self):
        errMsg = _('Invalid Request')
        return {'i18nMessage':zope.i18n.translate(errMsg, context=self.request)}


class MethodNotFoundView(JSONRPCErrorView):
    """Knows the error data for NotFound errors."""

    code = -32601
    message = u'Method not found'

    @property
    def data(self):
        errMsg = _('Method not found')
        return {'i18nMessage':zope.i18n.translate(errMsg, context=self.request)}


class InvalidParamsErrorView(JSONRPCErrorView):
    """Knows the error data for invalid params errors."""

    code = -32602
    message = u'Invalid params'

    @property
    def data(self):
        errMsg = _('Invalid params')
        return {'i18nMessage':zope.i18n.translate(errMsg, context=self.request)}


class InternalErrorView(JSONRPCErrorView):
    """Knows the error data for invalid params errors."""

    code = -32603
    message = u'Internal error'

    @property
    def data(self):
        errMsg = _('Internal error')
        return {'i18nMessage':zope.i18n.translate(errMsg, context=self.request)}
