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

from z3c.jsonrpc import interfaces


class IJSONRPCLayer(interfaces.IJSONRPCRequest):
    """Layer for JSONRPC requests.

    IMPORTANT:
    If you like to use ZPT templates and call adatapers in MethodPublisher 
    views, you need to make sure that your layer provides the relevant
    adapters. This means, you will probably use a layer inherited from 
    IBrowserRequest and IJSONRPCRequest in your skin.

    Or you can register your icons etc. for the IJSONRequest layer etc. if you
    need to return content produced by ZPT tempaltes. Also note that icons
    or other resources are only available in IBrowserRequest or in your custom
    layer.
    """
