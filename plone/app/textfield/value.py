from persistent import Persistent
from plone.app.textfield.interfaces import IRichTextValue
from plone.app.textfield.interfaces import ITransformer
from plone.base.utils import safe_text
from zope.component.hooks import getSite
from zope.interface import implementer

import logging

LOG = logging.getLogger("plone.app.textfield")

HTML_MIME_TYPE = "text/html"
SAFE_HTML_MIME_TYPE = "text/x-html-safe"


class RawValueHolder(Persistent):
    """Place the raw value in a separate persistent object so that it does not
    get loaded when all we want is the output.
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "<RawValueHolder: %s>" % self.value

    def __eq__(self, other):
        if not isinstance(other, RawValueHolder):
            return NotImplemented
        return self.value == other.value

    def __ne__(self, other):
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


@implementer(IRichTextValue)
class RichTextValue:
    """The actual value.

    Note that this is not a persistent object, to avoid a separate ZODB object
    being loaded.
    """

    def __init__(
        self,
        raw=None,
        mimeType=None,
        outputMimeType=None,
        encoding="utf-8",
        output=None,
    ):
        self._raw_holder = RawValueHolder(raw)
        self._mimeType = mimeType
        self._outputMimeType = outputMimeType
        self._encoding = encoding

    # the raw value - stored in a separate persistent object

    @property
    def raw(self):
        return self._raw_holder.value

    # Encoded raw value

    @property
    def encoding(self):
        return self._encoding

    @property
    def raw_encoded(self):
        if self._raw_holder.value is None:
            return ""
        happy_value = safe_text(self._raw_holder.value, encoding=self.encoding)
        return happy_value.encode(self.encoding, "ignore")

    # the current mime type
    @property
    def mimeType(self):
        return self._mimeType

    # the default mime type

    @property
    def outputMimeType(self):
        return self._outputMimeType

    def _clone_for_transform(self, mimeType, outputMimeType):
        clone = self.__class__.__new__(self.__class__)
        clone._raw_holder = self._raw_holder
        clone._mimeType = mimeType
        clone._outputMimeType = outputMimeType
        clone._encoding = self.encoding
        return clone

    @property
    def output(self):
        site = getSite()
        return self.output_relative_to(site)

    def output_relative_to(self, context):
        """Transforms the raw value to the output mimetype, within a specified context.

        If the value's mimetype is already the same as the output mimetype,
        no transformation is performed unless safe HTML output is requested.

        The context parameter is relevant when the transformation is
        context-dependent. For example, Plone's resolveuid-and-caption
        transform converts relative links to absolute links using the context
        as a base.

        If a transformer cannot be found for the specified context, a
        transformer with the site as a context is used instead.
        """
        if self.raw is None:
            return None

        mimeType = self.mimeType or HTML_MIME_TYPE
        outputMimeType = self.outputMimeType or SAFE_HTML_MIME_TYPE

        if mimeType == outputMimeType and outputMimeType != SAFE_HTML_MIME_TYPE:
            return self.raw

        if mimeType == SAFE_HTML_MIME_TYPE and outputMimeType == SAFE_HTML_MIME_TYPE:
            # Treat stored safe HTML as HTML when rendering to the safe HTML
            # output type.  The safe_html transform is idempotent for already
            # safe markup, and this avoids trusting attacker-controlled input
            # that merely claims to be text/x-html-safe.
            mimeType = HTML_MIME_TYPE

        transformer = ITransformer(context, None)
        if transformer is None:
            site = getSite()
            transformer = ITransformer(site, None)
            if transformer is None:
                return None

        value = self
        if mimeType != self.mimeType or outputMimeType != self.outputMimeType:
            value = self._clone_for_transform(mimeType, outputMimeType)

        return transformer(value, outputMimeType)

    def __repr__(self):
        return (
            "RichTextValue object. (Did you mean <attribute>.raw or "
            "<attribute>.output?)"
        )

    def __eq__(self, other):
        if not isinstance(other, RichTextValue):
            return NotImplemented
        return vars(self) == vars(other)

    def __ne__(self, other):
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal

    def getSize(self):
        return len(safe_text(self.raw).encode("utf-8"))
