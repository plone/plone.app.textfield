Introduction
============

This package provides a zope.schema style field type called RichText which
can be used to store a value with a related MIME type. The value can be
transformed to an output MIME type, for example to transform from structured
text to HTML.

To use the field, place it in a schema like so::

    from plone.app.textfield import RichText
    from zope.interface import Interface
    
    class ITest(Interface):
    
        bodyText = RichText(
                title=u"Body text",
                default_mime_type='text/structured',
                output_mime_type='text/html',
                allowed_mime_types=('text/structured', 'text/plain',),
                default=u"Default value"
            )

This specifies the default MIME type of text content as well as the default
output type, and a tuple of allowed types. All these values are optional.
The default MIME type is 'text/html', and the default output type is
'text/x-html-safe'. By default, allowed_mime_types is None, which means
no validation will take place on the allowed MIME type.

Note that the default value here is set to a unicode string, which will be
considered to be of the default MIME type. This value is converted to a
`RichTextValue` object (see below) on field initialisation, so the `default`
property will be an object of this type.

The field actually stores an object of type
`plone.app.textfield.value.RichTextValue`. This object has the following
attributes:

    raw (read/write)
        The raw value as a unicode string. This value is stored in a ZODB
        blob.
    
    mimeType (read/write)
        The MIME type of the raw text.
    
    output (read-only)
        A unicode string that represents the value transformed to the
        default output MIME type. This is not stored in a BLOB. May be None
        if the transformation could not be completed successfully.
        
    readonly (read-only)
        The value may be read-only. A common example is the `default` property
        on the field, if set. In this case, setting the raw value or MIME
        type will result in a TypeError. Use the copy() method to get back
        a new copy that is not in read-only mode.

The idea is that the raw value is used in edit controls or if a different
transformation is required. The output value is stored in a non-BLOB string,
because it is expected to be commonly used (e.g. as the body text of a page-
like object) and should thus be loaded with the object.

The RichTextValue is not a persistent object, but is expected to be set as
an attribute of a persistent object. It will notify its parent (via the
_p_changed protocol) when it is modified. The parent will be set correctly
when the field's set() method is used. Otherwise, set it yourself.

Transformation takes place using an ITransformer adapter. The default
implementation uses Plone's portal_transforms tool to convert form one
MIME type to another. Note that Products.PortalTransforms must be installed
for this to work, otherwise no default ITransformer adapter is registered.
You can use the [portaltransforms] extra to add a `Products.PortralTransforms`
dependency.

The package also contains a `plone.supermodel` export/import handler, which
will be configured if plone.supermodel is installed. You can use the
[supermodel] extra to add a `plone.supermodel` dependency.

Finally, a `z3c.form` widget will be installed if `z3c.form` is installed.
The [widget] extra will pull this dependency in if nothing else does.

See field.txt for more details about the field's behaviour, and handler.txt
for more details about the plone.supermodel handler.
