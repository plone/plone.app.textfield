# -*- coding: utf-8 -*-
from plone.app.textfield import _
from plone.app.textfield import interfaces
from plone.app.textfield import RichText
from plone.schemaeditor.fields import FieldFactory
from zope import schema
from zope.interface import Attribute
from zope.schema import interfaces as schema_ifaces


try:
    import plone.app.vocabularies  # noqa
    HAS_VOCABS = True
except ImportError:
    HAS_VOCABS = False


class IRichText(interfaces.IRichText, schema_ifaces.IFromUnicode):

    if HAS_VOCABS:
        default_mime_type = schema.Choice(
            title=_(u'Input format'),
            vocabulary='plone.app.vocabularies.AllowedContentTypes',
            default='text/html',
        )
    else:
        default_mime_type = Attribute('')

    # prevent some settings from being included in the field edit form
    default = Attribute('')
    output_mime_type = Attribute('')
    allowed_mime_types = Attribute('')

RichTextFactory = FieldFactory(RichText, _(u'Rich Text'))
