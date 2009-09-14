from zope.interface import implements
from zope.component import adapts

from zope.app.component.hooks import getSite
from zExceptions import ConflictError

from plone.app.textfield.interfaces import ITransformer, TransformError

from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName

class PortalTransformsTransformer(object):
    """Invoke portal_transforms to perform a conversion
    """
    
    implements(ITransformer)
    adapts(IContentish)
    
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
            data = transforms.convertTo(mimeType, value.raw_encoded, mimetype=value.mimeType,
                                        object=self.context, encoding=value._encoding)
            output = data.getData()
            return output.decode(value._encoding)
        except ConflictError:
            raise
        except Exception, e:
            raise TransformError("Error during transformation", e)
