try:
    from plone.supermodel.exportimport import BaseHandler
    HAVE_SUPERMODEL = True
except ImportError:
    HAVE_SUPERMODEL = False
    
if HAVE_SUPERMODEL:

    
    from plone.app.textfield import RichText
    
    class RichTextHandler_(BaseHandler):
        """Special handling for the RichText field, to deal with 'default'
        that may be unicode.
        """
    
        # Don't read or write 'schema'
        filteredAttributes = BaseHandler.filteredAttributes.copy()
        filteredAttributes.update({'schema': 'rw'})
    
        def __init__(self, klass):
            super(RichTextHandler_, self).__init__(klass)
        
        # TODO: when reading 'default', allow a string; when writing 'default', 
        # skip unless of default mime type
    
    RichTextHandler = RichTextHandler_(RichText)
