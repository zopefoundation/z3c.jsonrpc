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


class UnauthorizedResponse(object):
    """Knows how to return error content."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        errMsg = _('You are not allowed to access this content.')
        return zope.i18n.translate(errMsg, context=self.request)
