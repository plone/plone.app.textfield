import logging

from zope.interface import implements
from zope.app.component.hooks import getSite

from plone.app.textfield.interfaces import IRichTextValue, ITransformer, TransformError

from ZODB.blob import Blob

LOG = logging.getLogger('plone.app.textfield')

class RichTextValue(object):
    """The actual value.
    
    Note that this is not a persistent object, to avoid a separate ZODB object
    being loaded.
    """
    
    implements(IRichTextValue)
    
    def __init__(self, raw=None, mimeType=None, outputMimeType=None, encoding='utf-8', output=None):
        self._blob           = Blob()
        self._mimeType       = mimeType
        self._outputMimeType = outputMimeType
        self._encoding       = encoding
        self._output         = output
        
        raw_encoded = raw.encode(self._encoding)
        
        fp = self._blob.open('w')
        try:
            fp.write(raw_encoded)
            self._set = True
        finally:
            fp.close()
        
        if output is None:
            self._update(raw_encoded)
    
    # output: the cached transformed value. Not stored in a BLOB since it
    # is probably used on the main view of the object and should thus be
    # loaded with the object
    
    @property
    def output(self):
        if self._output is None:
            self._update(self.raw_encoded)
        return self._output
        
    # the raw value - stored in a BLOB
    
    @property
    def raw(self):
        value = self.raw_encoded
        return value.decode(self._encoding)
    
    # Encoded raw value

    @property
    def encoding(self):
        return self._encoding

    @property
    def raw_encoded(self):
        fp = self._blob.open('r')
        try:
            return fp.read()
        finally:
            fp.close()
    
    # the current mime type
    
    @property
    def mimeType(self):
        return self._mimeType

    # the default mime type
    
    @property
    def outputMimeType(self):
        return self._outputMimeType
    
    # cached output
    
    def _update(self, raw_encoded):
        """Update the cache
        """
        
        site = getSite()
        transformer = ITransformer(site, None)
        if transformer is None:
            return
        
        try:
            self._output = transformer(self, self.outputMimeType)
        except TransformError, e:
            self._output = None
    
    def __repr__(self):
        return u"RichTextValue object. (Did you mean <attribute>.raw or <attribute>.output?)"
