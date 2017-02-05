Changelog
=========

1.2.8 (2017-02-05)
------------------

New features:

- Enable the ``RichText`` field to work together with a simple ``ITextAreaWidget``.
  [jensens]


Bug fixes:

- Cleanup:
  Use more zope.interface decorators,
  add utf8 headers,
  isort imports,
  zcml conditions are enough.
  [jensens]


1.2.7 (2016-08-10)
------------------

Fixes:

- Use zope.interface decorator.
  [gforcada]


1.2.6 (2015-05-31)
------------------

- Fix negative equality bug RawValueHolder and RichTextValue introduced in 1.2.5.
  [jone]


1.2.5 (2015-03-26)
------------------

- Add equality check (`__eq__`) for RawValueHolder and RichTextValue;
  [davisagli]

- Fix marshaler decode to always decode raw value into unicode
  [datakurre]

- Remove utils.getSiteEncoding, which was deprecated and not used anywhere.
  [thet]

- For Plone 5, support getting markup control panel settings from the registry,
  while still supporting normal portal_properties access for Plone < 5.
  [thet]

- Resolved an interesting circular import case, which wasnt effective because
  of sort order of imports
  [thet]


1.2.4 (2014-10-20)
------------------

* Force WYSIWYG, so when we start with 'text/plain' (or another MIME),
  selecting 'text/html' will cause TinyMCE to spring into life.
  [lentinj]

* Tell Products.TinyMCE what the MIME type is, so it doesn't have to work it out.
  [lentinj]

- Use closest_content to navigate through the sea of subforms to
  find something that we can use portal_url on.
  [lentinj]

- Do not give an error when the raw value is not unicode and isn't
  ascii. In that case, encode as unicode then decode as the proper
  string, bang head on desk.
  [eleddy]

- Internationalization.
  [thomasdesvenain]


1.2.3 (2014-01-27)
------------------

- Do not give an error when the raw value is None.  Give an empty
  unicode string as output in that case.
  [maurits]


1.2.2 (2013-01-01)
------------------

* Add support for collective.ckeditor.
  [tschorr]

1.2.1 (2012-08-14)
------------------

* Fix compatibility with Zope 2.12. [davisagli]


1.2 (2012-08-14)
----------------

* Pass field's max_length to the wysiwyg macro, if it has one.
  [davisagli]

* Determine which editor's wysiwyg_support template to use from within
  widget_input.pt. Fixes support for collective.ckeditor.
  [tschorr, davisagli]

* Update getSite import locations.
  [hannosch]

* Make sure that the display widget absolutizes relative links relative
  to the correct context. To facilitate doing this from custom templates,
  RichTextValue now has an ``output_relative_to`` helper method which
  can be passed a context.
  [davisagli]

* Fix an issue with the support for plone.schemaeditor.
  [davisagli]

* Support a ``max_length`` parameter for RichText fields. Input longer
  than the max_length does not pass validation.
  [davisagli]

* Pass some additional context to the wysiwyg_support macro to help with
  determining the field's mimetype.
  [davisagli]

* Changed deprecated getSiteEncoding to hardcoded `utf-8`
  [tom_gross]

1.1 - 2012-02-20
----------------

* Provide a version of the RichText field schema for use with
  plone.schemaeditor. Only the ``default_mime_type`` field is exposed for
  editing through-the-web, with a vocabulary of mimetypes derived from
  the ``AllowedContentTypes`` vocabulary in ``plone.app.vocabularies``
  (which can be adjusted via Plone's markup control panel).
  [davisagli]

* Log original exception when a TransformError is raised.
  [rochecompaan]

1.0.2 - 2011-11-26
------------------

* If no transform path is found: Instead of throwing an exception page
  in the face of the user, now return an empty string and log error message.
  [kleist]

* Fix infinite recursion bug when source and target mimetype is the
  same. [rochecompaan]

1.0.1 - 2011-09-24
------------------

* Make sure the field constraint is validated, if specified.
  This closes http://code.google.com/p/dexterity/issues/detail?id=200
  [davisagli]

* Make sure validation fails if no text is entered for a required field.
  This closes http://code.google.com/p/dexterity/issues/detail?id=199
  [davisagli]

* Wrap the context in the form context, not the site, so that relative links
  are generated correctly.
  [davisagli]

* Avoid duplicating the id of the textarea if the form has no prefix.
  [davisagli]

* Fix case where editor did not load if the context being edited is a
  dict.
  [davisagli]

* Pass through the z3c.form widget's ``rows`` and ``cols`` settings to the
  wysiwyg editor macro.
  [davisagli]

1.0 - 2011-04-30
----------------

* Fix failing test.
  [davisagli]

1.0b7 - 2011-02-11
------------------

* Don't persistently cache output. Transforms may depend on outside state
  (e.g. the uuid transform.) PortalTransform's caching is imperfect, but it is
  time limited. http://code.google.com/p/dexterity/issues/detail?id=151
  [elro]

* Pass context to portal transforms.
  [elro]

1.0b6 - 2010-04-18
------------------

* Fix the field schemata so they can be used as the form schema when adding the
  field using plone.schemaeditor
  [rossp]

* Remove unused lookup of the current member's editor preference. This is
  handled by the wysiwyg_support macros.
  [davisagli]

1.0b5 - 2009-11-17
------------------

* Fix an error that could occur if the user did not have an editor preference
  set.
  [optilude]

* Fix tests on Plone 4.
  [optilude]

* Add field factory for use with plone.schemaeditor (only configured if that
  package is installed).
  [davisagli]

1.0b4 - 2009-10-12
------------------

* Update README.txt to be in line with reality.
  [optilude]

* Fix the @@text-transform view to work with path traversal.
  [optilude]

1.0b3 - 2009-10-08
------------------

* Add plone.rfc822 field marshaller. This is only configured if that package
  is installed.
  [optilude]

1.0b2 - 2009-09-21
------------------

* Store the raw value in a separate persistent object in the ZODB instead of
  in a BLOB. This avoids potential problems with having thousands of small
  BLOB files, which would not be very space efficient on many filesystems.
  [optilude]

* Make the RichTextValue immutable. This greatly simplifies the code and
  avoids the need to keep track of the parent object.
  [optilude]

1.0b1 - 2009-09-17
------------------

* Initial release
