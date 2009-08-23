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

import zope.schema
import zope.interface
from zope.publisher.interfaces import IPublication
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import ISkinnable
from zope.publisher.interfaces import ISkinType
from zope.publisher.interfaces.http import IHTTPApplicationRequest
from zope.publisher.interfaces.http import IHTTPCredentials
from zope.publisher.interfaces.http import IHTTPRequest
from zope.app.publication.interfaces import IRequestFactory

JSON_CHARSETS = ('utf-8','utf-16', 'utf-32')


class IMethodPublisher(zope.interface.Interface):
    """Marker interface for an object that wants to publish methods."""


class IJSONRPCRequestFactory(IRequestFactory):
    """Browser request factory"""


class IJSONRPCPublisher(IPublishTraverse):
    """JSON-RPC Publisher
    like zope.publisher.interfaces.xmlrpc.IXMLRPCPublisher
    """


class IJSONRPCPublication(IPublication):
    """Publication for JOSN-RPC-based protocol."""


class IJSONRPCSkinType(ISkinType):
    """A skin is a set of layers."""


class IJSONRPCApplicationRequest(IHTTPApplicationRequest):
    """HTTP application request."""


class IJSONRPCRequest(IJSONRPCApplicationRequest, IHTTPCredentials,
    IHTTPRequest, ISkinnable):
    """JSON-RPC request."""

    jsonID = zope.interface.Attribute("""JSON-RPC ID for the request""")


class IJSONRPCException(zope.interface.Interface):
    """JSON-RPC error"""


class IJSONRPCErrorView(zope.interface.Interface):
    """Error view base class used by ZopePublications error handling.
    """

    code = zope.schema.Int(
        title=u'Error code',
        description=u'JSON-RPC error code',
        default=-32603,
        required=True)

    message = zope.schema.Text(
        title=u'Error message',
        description=u'JSON-RPC error message',
        default=u'Internal error',
        required=True)

    data = zope.schema.Text(
        title=u'Error data',
        description=u'JSON-RPC error data',
        default=u'',
        required=True)

    def __init__(self):
        """Adapts an error and a request."""

    def __call__(self):
        """Must return itself by calling."""
