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


# The error codes used since JSON-RPC 2.0:
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

class JSONRPCException(Exception):
    """Base class for JSON-RPC exception."""


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
