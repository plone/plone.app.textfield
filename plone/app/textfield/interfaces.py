from zope.interface import Interface

from zope.schema.interfaces import IObject
from zope import schema

class IRichText(IObject):
    """A text field that stores MIME type
    """

    default_mime_type = schema.ASCIILine(
            title=u"Default MIME type",
            default='text/html',
        )
    
    output_mime_type = schema.ASCIILine(
            title=u"Deafult output MIME type",
            default='text/x-html-safe'
        )
    
    allowed_mime_types = schema.Tuple(
            title=u"Allowed MIME types",
            description=u"Set to None to disable checking",
            default=None,
            required=False,
            value_type=schema.ASCIILine(title=u"MIME type"),
        )

class IRichTextValue(Interface):
    """The value actually stored in a RichText field.
    
    This stores the following values on the parent object
    
      - A ZODB blob with the original value
      - A cache of the value transformed to the default output type
    """
    
    __parent__ = schema.Object(
            title=u"Content object",
            schema=Interface
        )
    
    mimeType = schema.ASCIILine(
            title=u"MIME type"
        )
    
    outputMimeType = schema.ASCIILine(
            title=u"Default output MIME type"
        )
    
    output = schema.Text(
            title=u"Transformed value in the target MIME type",
            readonly=True
        )
    
    raw = schema.Text(
            title=u"Raw value in the original MIME type"
        )
    
    readonly = schema.Bool(
            title=u"Is the value readonly? If so, setting the raw data will raise a TypeError."
        )
        
    def modified():
        """Notify the parent (if set) that this object has been modified
        """
    
    def update():
        """Updated the cached output value
        """
    
    def copy(parent=None):
        """Return a copy of this value, with the given parent
        """

class TransformError(Exception):
    """Exception raised if a value could not be transformed. This is normally
    caused by another exception. Inspect self.cause to find that.
    """
    
    def __init__(self, message, cause=None):
        self.message = message
        self.cause = cause
    
    def __str__(self):
        return self.message

class ITransformer(Interface):
    """A simple abstraction for invoking a transformation from one MIME
    type to another.
    
    This is not intended as a general transformations framework, but rather
    as a way to abstract away a dependency on the underlying transformation
    engine.
    
    This interface will be implemented by an adapter onto the context where
    the value is stored.
    """
    
    def __call__(value, mimeType):
        """Transform the IRichTextValue 'value' to the given MIME type.
        Return a unicode string. Raises TransformError if something went
        wrong.
        """
