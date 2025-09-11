from plone.base.interfaces import IEditingSchema
from plone.base.interfaces import IMarkupSchema
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface.interfaces import ComponentLookupError


def markupRegistrySettings(context):
    if not IMarkupSchema:
        return None
    try:
        # get the new registry
        registry = getUtility(IRegistry, context=context)
        settings = registry.forInterface(
            IMarkupSchema,
            prefix="plone",
        )
    except (KeyError, ComponentLookupError):
        settings = None
    return settings


def getAllowedContentTypes():
    """Get a set of allowed MIME types."""
    site = getSite()
    if site is None:
        return None

    reg = markupRegistrySettings(site)
    if reg:
        return reg.allowed_types
    portal_transforms = getToolByName(site, "portal_transforms", None)
    if portal_transforms is None:
        return None

    return set(portal_transforms.listAvailableTextInputs())


def getDefaultWysiwygEditor():
    registry = getUtility(IRegistry)
    try:
        records = registry.forInterface(IEditingSchema, check=False, prefix="plone")
        default_editor = records.default_editor.lower()
    except AttributeError:
        default_editor = "tinymce"
    return default_editor


def getAvailableWysiwygEditors():
    registry = getUtility(IRegistry)
    try:
        records = registry.forInterface(IEditingSchema, check=False, prefix="plone")
        available = records.available_editors
    except AttributeError:
        available = ["TinyMCE"]
    return available


def getWysiwygEditor(member_editor, available_editors, default_editor):
    if member_editor is None:
        return default_editor.lower()
    elif member_editor == "None":
        return "plaintexteditor"
    elif member_editor in available_editors:
        return member_editor.lower()
    else:
        # Member's wysiwyg_editor property holds
        # wysiwyg_editor that has been uninstalled
        return default_editor.lower()
