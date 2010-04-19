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
'text/x-html-safe'. By default, ``allowed_mime_types`` is None, which means
that the side-wide default set of allowable input MIME types will be permitted.

Note that the default value here is set to a unicode string, which will be
considered to be of the default MIME type. This value is converted to a
``RichTextValue`` object (see below) on field initialisation, so the
``default`` property will be an object of this type.

The field actually stores an immutable object of type
`plone.app.textfield.value.RichTextValue`. This object has the following
attributes:

    raw
        The raw value as a unicode string.
    
    mimeType
        The MIME type of the raw text.
    
    output
        A unicode string that represents the value transformed to the
        default output MIME type. May be None if the transformation could
        not be completed successfully, but will be cached after it has been
        successfully transformed once.
        
    outputMimeType
        The MIME type of the output string. This is normally copied from the
        field's ``output_mime_type`` property.

That the ``output``, ``mimeType`` and ``outputMimeType`` properties will be
stored in the same _p_jar as the parent content object, whilst the ``raw``
value is stored in a separate persistent object. This is to optimise for the
common case where the ``output`` is frequently accessed when the object is
viewed (and thus should avoid a separate persistent object load), whereas the
``raw`` value is infrequently accessed (and so should not take up memory
unless specifically requested).

Transformation takes place using an ``ITransformer`` adapter. The default
implementation uses Plone's ``portal_transforms`` tool to convert form one
MIME type to another. Note that ``Products.PortalTransforms`` must be installed
for this to work, otherwise no default ITransformer adapter is registered.
You can use the ``[portaltransforms]`` extra to add
``Products.PortralTransforms`` as a dependency.

To invoke alternative transformations from a page template, you can use the
following convenience syntax::

  <div tal:content="structure context/@@text-transform/fieldName/text/plain" />
  
Here ``fieldName`` is the name of the field (which must be found on ``context``
and contain a ``RichTextValue``). ``text/plain`` is the desired output MIME
type.

The package also contains a ``plone.supermodel`` export/import handler, which
will be configured if plone.supermodel is installed. You can use the
``[supermodel]`` extra to add a ``plone.supermodel`` dependency.

A ``z3c.form`` widget will be installed if `z3c.form`` is installed.
The ``[widget]`` extra will pull this dependency in if nothing else does.

A ``plone.rfc822`` field marshaler will be installed if ``plone.rfc822`` is
installed. The ``[marshaler]`` extra will pull this dependency in if nothing
else does.

A ``plone.schemaeditor`` field factory will be installed if
``plone.schemaeditor`` is installed. The ``editor`` extra will pull this
dependency if nothing else does.

See field.txt for more details about the field's behaviour, and handler.txt
for more details about the plone.supermodel handler.
