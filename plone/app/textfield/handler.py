# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.app.textfield.interfaces import IRichText
from plone.supermodel.exportimport import BaseHandler
from plone.supermodel.interfaces import IToUnicode
from zope.component import adapter
from zope.interface import implementer


class RichTextHandler_(BaseHandler):
    """Special handling for the RichText field, to deal with 'default'
    that may be unicode.
    """

    # Don't read or write 'schema'
    filteredAttributes = BaseHandler.filteredAttributes.copy()
    filteredAttributes.update({'schema': 'rw'})

    def __init__(self, klass):
        super(RichTextHandler_, self).__init__(klass)


@implementer(IToUnicode)
@adapter(IRichText)
class RichTextToUnicode(object):

    def __init__(self, context):
        self.context = context

    def toUnicode(self, value):
        return value.raw


RichTextHandler = RichTextHandler_(RichText)
