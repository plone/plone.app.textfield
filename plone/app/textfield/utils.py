from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

def getSiteEncoding(default='utf-8'):
    """Get the default site encoding
    """
    site = getSite()
    if site is None:
        return default
    
    portal_properties = getToolByName(site, 'portal_properties', None)
    if portal_properties is None:
        return default
    
    site_properties = portal_properties.get('site_properties', None)
    if site_properties is None:
        return default
    
    return site_properties.getProperty('site_encoding', default)
