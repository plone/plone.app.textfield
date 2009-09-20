import logging

from rwproperty import getproperty, setproperty

from zope.interface import implements
from zope.app.component.hooks import getSite

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
    
    def __init__(self, parent=None, outputMimeType=None, raw=None,
                 mimeType=None, encoding='utf-8', readonly=False):
        self.__parent__ = parent
        self._blob = Blob()
        self._outputMimeType = outputMimeType
        self._set = False
        self._mimeType = mimeType
        self._output = None
        self._encoding = encoding
        self._readonly = readonly
        
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
        
        if self.readonly:
            raise TypeError("Value is readonly. Use copy() first.")
        
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
        
        if self.readonly:
            raise TypeError("Value is readonly. Use copy() first.")
        
        self._mimeType = value
        self.update()
        self.modified()
    
    # the default mime type
    
    @getproperty
    def outputMimeType(self):
        return self._outputMimeType
    
    @setproperty
    def outputMimeType(self, value):
        
        if self.readonly:
            raise TypeError("Value is readonly. Use copy() first.")
        
        self._outputMimeType = value
        self.update()
        self.modified()
    
    # is the object readonly?
    @getproperty
    def readonly(self):
        return self._readonly
    
    @setproperty
    def readonly(self, value):
        self._readonly = value
        self.modified()
    
    # cached output
    
    def update(self):
        """Update the cache
        """
        
        if not self._set:
            return
        
        if self.outputMimeType is None:
            return
        
        context = self.__parent__
        if context is None:
            context = getSite()
        
        transformer = ITransformer(context, None)
        if transformer is None:
            return
            
        try:
            self._output = transformer(self, self.outputMimeType)
        except TransformError, e:
            self._output = None
        self.modified()
    
    def modified(self):
        """Notify the parent that the value has been modified
        """
        if self.__parent__ is not None:
            self.__parent__._p_changed = 1
    
    def copy(self, parent=None, readonly=False):
        """Return a copy of this value, without the given parent.
        """
        newvalue = RichTextValue(parent)
        newvalue._blob = Blob()
        newvalue._outputMimeType = self.outputMimeType
        newvalue._mimeType = self.mimeType
        newvalue._output = self._output
        newvalue._encoding = self._encoding
        newvalue._readonly = readonly
        
        fp = newvalue._blob.open('w')
        try:
            fp.write(self.raw_encoded)
        finally:
            fp.close()
        
        newvalue._set = True
        newvalue.modified()
        
        return newvalue
    
    def __repr__(self):
        return u"RichTextValue object. (Did you mean <attribute>.raw or <attribute>.output?)"
