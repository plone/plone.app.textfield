import urllib
from zope.interface import implements

from zope.publisher.interfaces import IPublishTraverse

from Acquisition import aq_inner
from Products.Five.browser import BrowserView

from plone.app.textfield.interfaces import ITransformer

class Transform(BrowserView):
    """Invoke a transformation on a RichText field.
    
    Invoke as:
    
        context/@@text-transform/fieldname
    
    Or:
    
        context/@@apply-transform/fieldname/mimetype
    
    The mimetype may be url quoted, e.g.
    
        context/@@apply-transform/fieldname/text%2Fplain
    """
    
    implements(IPublishTraverse)
    
    fieldName = None
    mimeType = None
    
    def publishTraverse(self, request, name):
        if self.fieldName is None:
            self.fieldName = name
        elif self.mimeType is None:
            self.mimeType = urllib.unquote_plus(name)
        return self
        
    def __call__(self, value=None, fieldName=None, mimeType=None):
        context = aq_inner(self.context)
        
        if fieldName is None:
            fieldName = self.fieldName
        
        if value is None:
            value = getattr(context, fieldName)
        
        if mimeType is None:
            mimeType = self.mimeType
            if mimeType is None:
                mimeType = value.outputMimeType
        
        transformer = ITransformer(context)
        return transformer(value, mimeType)
