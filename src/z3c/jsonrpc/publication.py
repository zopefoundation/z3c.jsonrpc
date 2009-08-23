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
import zope.component
from zope.app.publication.http import BaseHTTPPublication
from zope.app.publication.interfaces import IRequestPublicationFactory
from zope.app.publication.interfaces import IPublicationRequestFactory

from z3c.jsonrpc import interfaces
from z3c.jsonrpc.publisher import JSONRPCRequest


class JSONRPCPublication(BaseHTTPPublication):
    """JSON RPC Publication."""

    zope.interface.implements(interfaces.IJSONRPCPublication)


class JSONRPCFactory(object):
    zope.interface.implements(IRequestPublicationFactory)
    
    def canHandle(self, environment):
        return True
        
    def __call__(self):
        request_class = zope.component.queryUtility(
            interfaces.IJSONRPCRequestFactory, default=JSONRPCRequest)
        return request_class, JSONRPCPublication
