from zope.schema import interfaces as schema_ifaces

from plone.app.textfield import interfaces
from plone.app.textfield import RichText
from plone.schemaeditor.fields import FieldFactory

class IRichText(interfaces.IRichText, schema_ifaces.IFromUnicode):

    default = RichText(
        title=interfaces.IRichText['default'].title,
        description=interfaces.IRichText['default'].description,
        required=False)

    missing_value = RichText(
        title=interfaces.IRichText['missing_value'].title,
        description=interfaces.IRichText['missing_value'].description,
        required=False)

RichTextFactory = FieldFactory(RichText, u'Rich Text')
