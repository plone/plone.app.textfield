import logging

from plone.app.textfield.interfaces import ITransformer, TransformError
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError
from zope.app.component.hooks import getSite
from zope.interface import implements

LOG = logging.getLogger('plone.app.textfield')

class PortalTransformsTransformer(object):
    """Invoke portal_transforms to perform a conversion
    """

    implements(ITransformer)

    def __init__(self, context):
        self.context = context

    def __call__(self, value, mimeType):

        # shortcut if we already have the right value
        if mimeType is value.mimeType:
            return value.output

        site = getSite()

        transforms = getToolByName(site, 'portal_transforms', None)
        if transforms is None:
            raise TransformError("Cannot find portal_transforms tool")

        try:
            data = transforms.convertTo(mimeType,
                                        value.raw_encoded,
                                        mimetype=value.mimeType,
                                        context=self.context,
                                        # portal_transforms caches on this
                                        object=value._raw_holder,
                                        encoding=value.encoding)
            if data is None:
                LOG.error('No transform path found from "%s" to "%s".' %
                          (value.mimeType, mimeType))
                return u''; # TODO: error message instead?
            else:
                output = data.getData()
                return output.decode(value.encoding)
        except ConflictError:
            raise
        except Exception, e:
            raise TransformError('Error during transformation', e)
