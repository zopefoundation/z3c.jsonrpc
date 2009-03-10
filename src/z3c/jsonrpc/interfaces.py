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
