# -*- coding: utf-8 -*-
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.rfc822.defaultfields import BaseFieldMarshaler
from zope.component import adapter
from zope.interface import Interface


@adapter(Interface, IRichText)
class RichTextFieldMarshaler(BaseFieldMarshaler):
    """Field marshaler for plone.app.textfield values.
    """

    ascii = False

    def encode(self, value, charset='utf-8', primary=False):
        if value is None:
            return
        return value.raw.encode(charset)

    def decode(
            self,
            value,
            message=None,
            charset='utf-8',
            contentType=None,
            primary=False):
        try:
            unicode_value = value.decode(charset)
        except UnicodeEncodeError:
            unicode_value = value  # was already unicode
        return RichTextValue(
            raw=unicode_value,
            mimeType=contentType or self.field.default_mime_type,
            outputMimeType=self.field.output_mime_type,
            encoding=charset
        )

    def getContentType(self):
        value = self._query()
        if value is None:
            return None
        return value.mimeType

    def getCharset(self, default='utf-8'):
        value = self._query()
        if value is None:
            return None
        return value.encoding
