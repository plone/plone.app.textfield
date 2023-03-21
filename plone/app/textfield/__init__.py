from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.interfaces import IRichTextValue
from plone.app.textfield.value import RichTextValue
from zope.i18nmessageid.message import MessageFactory
from zope.interface import implementer
from zope.interface import Invalid
from zope.schema import Object
from zope.schema._bootstrapinterfaces import ConstraintNotSatisfied
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import WrongType


_ = MessageFactory("plone")


@implementer(IRichText, IFromUnicode)
class RichText(Object):
    """Text field that also stores MIME type"""

    default_mime_type = "text/html"
    output_mime_type = "text/x-html-safe"
    allowed_mime_types = None
    max_length = None

    def __init__(
        self,
        default_mime_type="text/html",
        output_mime_type="text/x-html-safe",
        allowed_mime_types=None,
        max_length=None,
        schema=IRichTextValue,
        **kw,
    ):
        self.default_mime_type = default_mime_type
        self.output_mime_type = output_mime_type
        self.allowed_mime_types = allowed_mime_types
        self.max_length = max_length

        if "default" in kw:
            default = kw["default"]
            if isinstance(default, str):
                kw["default"] = self.fromUnicode(default)
                kw["default"].readonly = True

        super().__init__(schema=schema, **kw)

    def fromUnicode(self, str_val):
        return RichTextValue(
            raw=str_val,
            mimeType=self.default_mime_type,
            outputMimeType=self.output_mime_type,
            encoding="utf-8",
        )

    def _validate(self, value):
        if self.allowed_mime_types and value.mimeType not in self.allowed_mime_types:
            raise WrongType(value, self.allowed_mime_types)

        if self.max_length is not None and len(value.raw) > self.max_length:
            raise Invalid(
                _(
                    "msg_text_too_long",
                    default="Text is too long. (Maximum ${max} characters.)",
                    mapping={"max": self.max_length},
                )
            )

        if not self.constraint(value):
            raise ConstraintNotSatisfied(value)
