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
import zope.traversing.namespace
from zope.location.interfaces import LocationError
from zope.publisher.skinnable import applySkin
from zope.component.interfaces import ComponentLookupError

from z3c.jsonrpc import interfaces


class skin(zope.traversing.namespace.view):
    """JSONRPC skin namespace"""

    def traverse(self, name, ignored):
        self.request.shiftNameToApplication()
        try:
            skin = zope.component.getUtility(interfaces.IJSONRPCSkinType, name)
        except ComponentLookupError:
            raise LocationError("++skin++%s" % name)
        applySkin(self.request, skin)
        return self.context
