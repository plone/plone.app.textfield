# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite


try:
    from Products.CMFPlone.interfaces import IEditingSchema
    from Products.CMFPlone.interfaces import IMarkupSchema
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility
    from zope.component.interfaces import ComponentLookupError
except ImportError:
    IMarkupSchema = None


def markupRegistrySettings(context):
    if not IMarkupSchema:
        return None
    try:
        # get the new registry
        registry = getUtility(IRegistry, context=context)
        settings = registry.forInterface(
            IMarkupSchema,
            prefix='plone',
        )
    except (KeyError, ComponentLookupError):
        settings = None
    return settings


def getAllowedContentTypes():
    """Get a set of allowed MIME types according to the portal_properties
    tool
    """
    site = getSite()
    if site is None:
        return None

    allowed_types = []
    reg = markupRegistrySettings(site)
    if reg:
        allowed_types = reg.allowed_types
    else:
        portal_transforms = getToolByName(site, 'portal_transforms', None)
        if portal_transforms is None:
            return None

        portal_properties = getToolByName(site, 'portal_properties', None)
        if portal_properties is None:
            return None

        site_properties = portal_properties.get('site_properties', None)
        if site_properties is None:
            return None

        allowed = set(portal_transforms.listAvailableTextInputs())
        forbidden = set(
            site_properties.getProperty('forbidden_contenttypes', []))

        allowed_types = allowed - forbidden

    return allowed_types


def getDefaultWysiwygEditor():
    registry = getUtility(IRegistry)
    try:
        records = registry.forInterface(IEditingSchema, check=False,
                                        prefix='plone')
        default_editor = records.default_editor.lower()
    except AttributeError:
        default_editor = 'tinymce'
    return default_editor


def getAvailableWysiwygEditors():
    registry = getUtility(IRegistry)
    try:
        records = registry.forInterface(IEditingSchema, check=False,
                                        prefix='plone')
        available = records.available_editors
    except AttributeError:
        available = ['TinyMCE']
    return available


def getWysiwygEditor(member_editor, available_editors, default_editor):
    if member_editor is None:
        return default_editor.lower()
    elif member_editor == u'None':
        return u'plaintexteditor'
    elif member_editor in available_editors:
        return member_editor.lower()
    else:
        # Member's wysiwyg_editor property holds
        # wysiwyg_editor that has been uninstalled
        return default_editor.lower()