import logging

from rwproperty import getproperty, setproperty

from zope.interface import implements
from plone.app.textfield.interfaces import IRichTextValue, ITransformer, TransformError

from ZODB.blob import Blob

LOG = logging.getLogger('plone.app.textfield')

class RichTextValue(object):
    """The actual value.
    
    Note that this is not a persistent object, to avoid a separate ZODB object
    being loaded. Instead, we store the value and set _p_changed on the
    parent (with the _p_jar), to which we keep a reference.
    """
    
    implements(IRichTextValue)
    
    def __init__(self, parent=None, defaultOutputMimeType=None, raw=None, mimeType=None, encoding='utf-8'):
        self.__parent__ = parent
        self._blob = Blob()
        self._defaultOutputMimeType = defaultOutputMimeType
        self._set = False
        self._mimeType = mimeType
        self._output = None
        self._encoding = encoding
        
        if raw:
            self.raw = raw
        
        self.modified()
    
    # output: the cached transformed value. Not stored in a BLOB since it
    # is probably used on the main view of the object and should thus be
    # loaded with the object
    
    @getproperty
    def output(self):
        return self._output
        
    # the raw value - stored in a BLOB
    
    @getproperty
    def raw(self):
        value = self.raw_encoded
        return value.decode(self._encoding)
    
    @setproperty
    def raw(self, value):
        assert isinstance(value, unicode)
        fp = self._blob.open('w')
        try:
            fp.write(value.encode(self._encoding))
            self._set = True
        finally:
            fp.close()
        self.update()
        self.modified()
    
    # Encoded raw value
    @getproperty
    def raw_encoded(self):
        fp = self._blob.open('r')
        try:
            return fp.read()
        finally:
            fp.close()
    
    # the current mime type
    
    @getproperty
    def mimeType(self):
        return self._mimeType
    
    @setproperty
    def mimeType(self, value):
        self._mimeType = value
        self.update()
        self.modified()
    
    # the default mime type
    
    @getproperty
    def defaultOutputMimeType(self):
        return self._defaultOutputMimeType
    
    @setproperty
    def defaultOutputMimeType(self, value):
        self._defaultOutputMimeType = value
        self.update()
        self.modified()
    
    # cached output
    
    def update(self):
        """Update the cache
        """
        
        if not self._set:
            return
        
        if self.defaultOutputMimeType is None:
            return
            
        transformer = ITransformer(self.__parent__, None)
        if transformer is None:
            return
            
        try:
            self._output = transformer(self, self.defaultOutputMimeType)
        except TransformError, e:
            self._output = None
        self.modified()
    
    def modified(self):
        """Notify the parent that the value has been modified
        """
        if self.__parent__ is not None:
            self.__parent__._p_changed = 1
    
    def __repr__(self):
        return u"RichTextValue object. (Did you mean <attribute>.raw or <attribute>.output?)"
