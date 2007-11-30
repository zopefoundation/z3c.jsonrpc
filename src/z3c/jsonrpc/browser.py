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

import zope.component
from zope.publisher.interfaces import NotFound
from z3c.jsonrpc.interfaces import IMethodPublisher


class JSONRPCTraversablePage(object):
    """Mixin for JSON-RPC traversable views, pages, forms etc.
    
    Make sure if you inherit from this class that no other super class
    will override the publishTraverse method.
    """

    def publishTraverse(self, request, name):
        view = zope.component.queryMultiAdapter((self, request), name=name)
        if view is None or not IMethodPublisher.providedBy(view):
            raise NotFound(self, name, request)
        return view
