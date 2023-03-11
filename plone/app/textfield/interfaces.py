from zope import schema
from zope.i18nmessageid.message import MessageFactory
from zope.interface import Interface
from zope.schema.interfaces import IObject


_ = MessageFactory("plone")


class IRichText(IObject):
    """A text field that stores MIME type"""

    default_mime_type = schema.ASCIILine(
        title=_("Default MIME type"),
        default="text/html",
    )

    output_mime_type = schema.ASCIILine(
        title=_("Default output MIME type"), default="text/x-html-safe"
    )

    allowed_mime_types = schema.Tuple(
        title=_("Allowed MIME types"),
        description=_("Set to None to disable checking"),
        default=None,
        required=False,
        value_type=schema.ASCIILine(title="MIME type"),
    )

    max_length = schema.Int(
        title=_("Maximum length"),
        description=_("in characters"),
        required=False,
        min=0,
        default=None,
    )


class IRichTextValue(Interface):
    """The value actually stored in a RichText field.

    This stores the following values on the parent object

      - A separate persistent object with the original value
      - A cache of the value transformed to the default output type

    The object is immutable.
    """

    raw = schema.Text(
        title=_("Raw value in the original MIME type"),
        readonly=True,
    )

    mimeType = schema.ASCIILine(
        title=_("MIME type"),
        readonly=True,
    )

    outputMimeType = schema.ASCIILine(
        title=_("Default output MIME type"),
        readonly=True,
    )

    encoding = schema.ASCIILine(
        title=_("Default encoding for the value"),
        description=_("Mainly used internally"),
        readonly=True,
    )

    raw_encoded = schema.ASCII(
        title=_("Get the raw value as an encoded string"),
        description=_("Mainly used internally"),
        readonly=True,
    )

    output = schema.Text(
        title=_("Transformed value in the target MIME type"),
        description=_("May be None if the transform cannot be completed"),
        readonly=True,
        required=False,
        missing_value=None,
    )


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
