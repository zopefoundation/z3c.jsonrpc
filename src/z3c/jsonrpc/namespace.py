import zope.component
import zope.interface
import zope.traversing.namespace
from zope.component.interfaces import ComponentLookupError
from zope.traversing.interfaces import TraversalError

from z3c.jsonrpc import interfaces


def applySkin(request, skin, skin_type):
       """Change the presentation skin for this request."""
       # Remove all existing skin declarations (commonly the default skin).
       ifaces = [iface for iface in zope.interface.directlyProvidedBy(request)
                 if not skin_type.providedBy(iface)]
       # Add the new skin.
       ifaces.append(skin)
       zope.interface.directlyProvides(request, *ifaces)


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
