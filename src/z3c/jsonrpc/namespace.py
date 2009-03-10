import zope.component
import zope.interface
import zope.traversing.namespace
from zope.location.interfaces import LocationError
from zope.publisher.skinnable import applySkin
from zope.component.interfaces import ComponentLookupError
from zope.traversing.interfaces import TraversalError

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
