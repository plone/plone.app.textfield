# -*- coding: utf-8 -*-
from Acquisition import ImplicitAcquisitionWrapper
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.interfaces import IRichTextValue
from plone.app.textfield.utils import getAllowedContentTypes
from plone.app.textfield.value import RichTextValue
from plone.app.z3cform.utils import closest_content
from UserDict import UserDict
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.browser.widget import addFieldClass
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITextAreaWidget
from z3c.form.interfaces import NOVALUE
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only


class IRichTextWidget(ITextAreaWidget):

    def allowedMimeTypes():
        """Get allowed MIME types
        """


@implementer_only(IRichTextWidget)
class RichTextWidget(TextAreaWidget):

    klass = u'richTextWidget'
    value = None

    def update(self):
        super(RichTextWidget, self).update()
        addFieldClass(self)

    def wrapped_context(self):
        context = self.context
        content = closest_content(context)
        # We'll wrap context in the current site *if* it's not already
        # wrapped.  This allows the template to acquire tools with
        # ``context/portal_this`` if context is not wrapped already.
        # Any attempts to satisfy the Kupu template in a less idiotic
        # way failed. Also we turn dicts into UserDicts to avoid
        # short-circuiting path traversal. :-s
        if context.__class__ == dict:
            context = UserDict(self.context)
        return ImplicitAcquisitionWrapper(context, content)

    def extract(self, default=NOVALUE):
        raw = self.request.get(self.name, default)

        if raw is default:
            return default

        mime_type = self.request.get(
            '{0:s}.mimeType'.format(self.name),
            self.field.default_mime_type
        )
        return RichTextValue(
            raw=raw,
            mimeType=mime_type,
            outputMimeType=self.field.output_mime_type,
            encoding='utf-8'
        )

    def allowedMimeTypes(self):
        allowed = self.field.allowed_mime_types
        if allowed is None:
            allowed = getAllowedContentTypes()
        return list(allowed)


@adapter(IRichText, IFormLayer)
@implementer(IFieldWidget)
def RichTextFieldWidget(field, request):
    """IFieldWidget factory for RichTextWidget."""
    return FieldWidget(field, RichTextWidget(request))


class RichTextConverter(BaseDataConverter):
    """Data converter for the RichTextWidget
    """

    def toWidgetValue(self, value):
        if IRichTextValue.providedBy(value):
            return value
        elif isinstance(value, unicode):
            return self.field.fromUnicode(value)
        elif value is None:
            return None
        raise ValueError(
            'Can not convert {0:s} to an IRichTextValue'.format(repr(value))
        )

    def toFieldValue(self, value):
        if IRichTextValue.providedBy(value):
            if value.raw == u'':
                return self.field.missing_value
            return value
        elif isinstance(value, unicode):
            if value == u'':
                return self.field.missing_value
            return self.field.fromUnicode(value)
        raise ValueError(
            'Can not convert {0:s} to an IRichTextValue'.format(repr(value))
        )


class RichTextAreaConverter(BaseDataConverter):
    """Data converter for the original z3cform TextWidget

    This converter ignores the fact allowed_mime_types might be set,
    because the widget has no way to select it.
    It always assumes the default_mime_type was used.
    """

    def toWidgetValue(self, value):
        if IRichTextValue.providedBy(value):
            if self.widget.mode in ('input', 'hidden'):
                return value.raw
            elif self.widget.mode == 'display':
                return value.output_relative_to(self.field.context)
        if isinstance(value, unicode):
            return value
        elif value is None:
            return None
        raise ValueError(
            'Can not convert {0:s} to unicode'.format(repr(value))
        )

    def toFieldValue(self, value):
        if value == u'':
            return self.field.missing_value
        elif isinstance(value, unicode):
            return RichTextValue(
                raw=value,
                mimeType=self.field.default_mime_type,
                outputMimeType=self.field.output_mime_type,
                encoding='utf-8'
            )
        elif IRichTextValue.providedBy(value):
            if value.raw == u'':
                return self.field.missing_value
            return value
        raise ValueError(
            'Can not convert {0:s} to an IRichTextValue'.format(repr(value))
        )
