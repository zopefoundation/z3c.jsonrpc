# Make a package.

import zope.component
import zope.traversing.namespace
from zope.component.interfaces import ComponentLookupError
from zope.publisher.http import applySkin
from zope.traversing.interfaces import TraversalError

from z3c.jsonrpc import interfaces


class skin(zope.traversing.namespace.skin):
    """JSONRPC skin type interface."""

    skin_type = interfaces.IJSONRPCSkinType

    def traverse(self, name, ignored):
        self.request.shiftNameToApplication()
        try:
            skin = zope.component.getUtility(self.skin_type, name)
        except ComponentLookupError:
            raise TraversalError("++skin++%s" % name)
        applySkin(self.request, skin, self.skin_type)
        return self.context
