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
import zope.configuration.fields
import zope.interface
import zope.schema
import zope.security.zcml
from zope.publisher.interfaces import IDefaultSkin

from zope.interface import Interface
from zope.security.checker import CheckerPublic, Checker
from zope.configuration.exceptions import ConfigurationError

from zope.component.interface import provideInterface
from zope.component.zcml import handler

from z3c.jsonrpc import interfaces
from z3c.jsonrpc.publisher import MethodPublisher


class IJSONRPCDirective(zope.interface.Interface):
    """Directive for JSONRPC methods."""

    for_ = zope.configuration.fields.GlobalObject(
        title=u"Published Object Type",
        description=u"""The types of objects to be published via JSONRPC

        This can be expressed with either a class or an interface
        """,
        required=True,
        )

    interface = zope.configuration.fields.Tokens(
        title=u"Interface to be published.",
        required=False,
        value_type=zope.configuration.fields.GlobalInterface()
        )

    methods = zope.configuration.fields.Tokens(
        title=u"Methods (or attributes) to be published",
        required=False,
        value_type=zope.configuration.fields.PythonIdentifier()
        )

    class_ = zope.configuration.fields.GlobalObject(
        title=u"Class",
        description=u"A class that provides attributes used by the view.",
        required=False
        )

    permission = zope.security.zcml.Permission(
        title=u"Permission",
        description=u"""The permission needed to use the view.

        If this option is used and a name is given for the view, then
        the names defined by the given methods or interfaces will be
        under the given permission.

        If a name is not given for the view, then, this option is required and
        the given permission is required to call the individual views defined
        by the given interface and methods.

        (See the name attribute.)

        If no permission is given, then permissions should be declared
        for the view using other means, such as the class directive.
        """,
        required=False)

    name = zope.schema.TextLine(
        title=u"The name of the view.",
        description=u"""

        If a name is given, then rpc methods are accessed by
        traversing the name and then accessing the methods.  In this
        case, the class should implement
        zope.pubisher.interfaces.IPublishTraverse.

        If no name is provided, then the names given by the attributes
        and interfaces are published directly as callable views.

        """,
        required=False,
        )

    layer = zope.configuration.fields.GlobalInterface(
        title=u"The layer the view is declared for",
        description=u"The default layer for which the default view is "
                    u"applicable. By default it is applied to all layers.",
        default=interfaces.IJSONRPCRequest,
        required=False
        )


def jsonrpc(_context, for_=None, interface=None, methods=None, class_=None,
    permission=None, name=None, layer=None):

    interface = interface or []
    methods = methods or []

    if layer is not None:
        if not layer.extends(interfaces.IJSONRPCRequest):
            raise ConfigurationError(
                "The layer interface must extend `IJSONRPCRequest`.")
    else:
        layer = interfaces.IJSONRPCRequest

    # If there were special permission settings provided, then use them
    if permission == 'zope.Public':
        permission = CheckerPublic

    require = {}
    for attr_name in methods:
        require[attr_name] = permission

    if interface:
        for iface in interface:
            for field_name in iface:
                require[field_name] = permission
            _context.action(
                discriminator = None,
                callable = provideInterface,
                args = ('', for_)
                )

    # Make sure that the class inherits MethodPublisher, so that the views
    # have a location
    if class_ is None:
        class_ = original_class = MethodPublisher
    else:
        original_class = class_
        class_ = type(class_.__name__, (class_, MethodPublisher), {})

    if name:
        # Register a single jsonrpc view

        if permission:
            checker = Checker(require)

            def proxyView(context, request, class_=class_, checker=checker):
                view = class_(context, request)
                # We need this in case the resource gets unwrapped and
                # needs to be rewrapped
                view.__Security_checker__ = checker
                return view

            class_ = proxyView
            class_.factory = original_class
        else:
            # No permission was defined, so we defer to the checker
            # of the original class
            def proxyView(context, request, class_=class_):
                view = class_(context, request)
                view.__Security_checker__ = getCheckerForInstancesOf(
                    original_class)
                return view
            class_ = proxyView
            class_.factory = original_class

        # Register the new view.
        _context.action(
            discriminator = ('jsonrpc', for_, name, layer),
            callable = handler,
            args = ('registerAdapter',
                    class_, (for_, layer), Interface, name,
                    _context.info)
            )
    else:
        if permission:
            checker = Checker({'__call__': permission})
        else:
            raise ConfigurationError(
              "JSONRPC view has neither a name nor a permission. "
              "You have to specify at least one of the two.")

        for name in require:
            # create a new callable class with a security checker;
            cdict = {'__Security_checker__': checker,
                     '__call__': getattr(class_, name)}
            new_class = type(class_.__name__, (class_,), cdict)
            _context.action(
                discriminator = ('jsonrpc', for_, name, layer),
                callable = handler,
                args = ('registerAdapter',
                        new_class, (for_, layer), Interface, name,
                        _context.info)
                )

    # Register the used interfaces with the site manager
    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )


class IDefaultJSONRPCSkinDirective(zope.interface.Interface):
    """Sets the default JSON-RPC skin."""

    name = zope.schema.TextLine(
        title=u"Default skin name",
        description=u"Default skin name",
        required=True
        )


def setDefaultJSONRPCSkin(name, info=''):
    """Set the default skin."""
    skin = zope.component.getUtility(interfaces.IJSONRPCSkinType, name=name)
    handler('registerAdapter', skin, (interfaces.IJSONRPCRequest,),
        IDefaultSkin, '', info),


def defaultJSONRPCSkin(_context, name):

    _context.action(
        discriminator = 'setDefaultJSONRPCSkin',
        callable = setDefaultJSONRPCSkin,
        args = (name, _context.info)
        )
