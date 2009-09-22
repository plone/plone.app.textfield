from zope.interface import implements

from zope.app.component.hooks import getSite
from ZODB.POSException import ConflictError

from plone.app.textfield.interfaces import ITransformer, TransformError

from Products.CMFCore.utils import getToolByName

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
                                        object=None, # stop portal_transforms from caching - we have our own cache in the 'output' variable
                                        encoding=value.encoding)
            output = data.getData()
            return output.decode(value.encoding)
        except ConflictError:
            raise
        except Exception, e:
            raise TransformError("Error during transformation", e)
