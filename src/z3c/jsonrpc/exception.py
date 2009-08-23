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

import zope.interface
from z3c.jsonrpc import interfaces


class JSONRPCException(Exception):
    """Base class for JSON-RPC exception."""

    zope.interface.implements(interfaces.IJSONRPCException)


class ParseError(JSONRPCException):
    """Invalid JSON. An error occurred on the server while parsing the JSON text."""


class InvalidRequest(JSONRPCException):
    """The received JSON not a valid JSON-RPC Request. """


class MethodNotFound(JSONRPCException):
    """The requested remote-procedure does not exist, is not available."""


class InvalidParams(JSONRPCException):
    """Invalid method parameters."""


class InternalError(JSONRPCException):
    """Internal JSON-RPC error."""
