# -*- coding: utf-8 -*-
from plone.app import testing
from plone.testing import layered

import doctest
import plone.app.textfield
import re
import six
import unittest


class IntegrationFixture(testing.PloneSandboxLayer):

    defaultBases = (testing.PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=plone.app.textfield)


PTC_FIXTURE = IntegrationFixture()
IntegrationLayer = testing.FunctionalTesting(
    bases=(PTC_FIXTURE,), name="PloneAppTextfieldTest:Functional"
)


class TestIntegration(unittest.TestCase):

    layer = IntegrationLayer

    def setUp(self):
        self.portal = self.layer["portal"]

    def testTransformPlain(self):
        from zope.interface import Interface
        from plone.app.textfield import RichText

        class IWithText(Interface):

            text = RichText(
                title=u"Text",
                default_mime_type="text/plain",
                output_mime_type="text/html",
            )

        value = IWithText["text"].fromUnicode(u"Some **text**")
        self.assertEquals(u"<p>Some **text**</p>", value.output)

    def testTransformNone(self):
        from plone.app.textfield.value import RichTextValue

        value = RichTextValue()
        # Mostly, these calls simply should not give an error.
        self.assertEquals(None, value.raw)
        if six.PY2:
            self.assertEquals(u"", value.output)
        else:
            self.assertEquals(None, value.output)

    def testTransformStructured(self):
        from zope.interface import Interface
        from plone.app.textfield import RichText

        class IWithText(Interface):

            text = RichText(
                title=u"Text",
                default_mime_type="text/structured",
                output_mime_type="text/html",
            )

        value = IWithText["text"].fromUnicode(u"Some **text**")
        self.assertEquals(u"<p>Some <strong>text</strong></p>\n", value.output)

    def testTransformView(self):
        from zope.interface import Interface, implementer
        from plone.app.textfield import RichText
        from Products.CMFCore.PortalContent import PortalContent

        class IWithText(Interface):

            text = RichText(
                title=u"Text",
                default_mime_type="text/structured",
                output_mime_type="text/html",
            )

        @implementer(IWithText)
        class Context(PortalContent):

            id = "context"
            text = None

        context = Context()
        context.text = IWithText["text"].fromUnicode(u"Some **text**")

        self.portal._setObject("context", context)
        context = self.portal["context"]

        output = context.restrictedTraverse("@@text-transform/text")()
        self.assertEquals(u"<p>Some <strong>text</strong></p>", output.strip())

        output = context.restrictedTraverse("@@text-transform/text/text/plain")()
        self.assertEquals(u"Some text", output.strip())

        # test transform shortcircuit when input and output type is the
        # same. this used to cause infinite recursion
        class IWithText(Interface):
            text = RichText(
                title=u"Text",
                default_mime_type="text/html",
                output_mime_type="text/html",
            )

        context.text = IWithText["text"].fromUnicode(u"<span>Some html</span>")
        output = context.restrictedTraverse("@@text-transform/text")()
        self.assertEquals(u"<span>Some html</span>", output.strip())

    def testTransformNoneView(self):
        from zope.interface import Interface, implementer
        from plone.app.textfield import RichText
        from plone.app.textfield.value import RichTextValue
        from Products.CMFCore.PortalContent import PortalContent

        class IWithText(Interface):

            text = RichText(
                title=u"Text",
                default_mime_type="text/structured",
                output_mime_type="text/html",
            )

        @implementer(IWithText)
        class Context(PortalContent):

            id = "context"
            text = None

        context = Context()
        # None as value should not lead to errors.
        context.text = RichTextValue()

        self.portal._setObject("context", context)
        context = self.portal["context"]

        output = context.restrictedTraverse("@@text-transform/text")()
        self.assertEquals(u"", output.strip())

        output = context.restrictedTraverse("@@text-transform/text/text/plain")()
        self.assertEquals(u"", output.strip())

    def testWidgetExtract(self):
        from zope.interface import Interface, implementer
        from plone.app.textfield import RichText
        from zope.publisher.browser import TestRequest
        from Products.CMFCore.PortalContent import PortalContent
        from plone.app.textfield.widget import RichTextWidget
        from z3c.form.widget import FieldWidget
        from z3c.form.interfaces import NOVALUE

        class IWithText(Interface):

            text = RichText(
                title=u"Text",
                default_mime_type="text/structured",
                output_mime_type="text/html",
            )

        @implementer(IWithText)
        class Context(PortalContent):

            text = None

        request = TestRequest()

        widget = FieldWidget(IWithText["text"], RichTextWidget(request))
        widget.update()

        value = widget.extract()
        self.assertEquals(NOVALUE, value)

        request.form["%s" % widget.name] = u"Sample **text**"
        request.form["%s.mimeType" % widget.name] = "text/structured"

        value = widget.extract()
        self.assertEquals(u"<p>Sample <strong>text</strong></p>", value.output.strip())

    def testRichTextWidgetConverter(self):
        from zope.interface import Interface
        from plone.app.textfield import RichText
        from zope.publisher.browser import TestRequest
        from plone.app.textfield.value import RichTextValue
        from plone.app.textfield.widget import RichTextWidget
        from plone.app.textfield.widget import RichTextConverter
        from z3c.form.widget import FieldWidget

        _marker = object()

        class IWithText(Interface):

            text = RichText(
                title=u"Text",
                default_mime_type="text/structured",
                output_mime_type="text/html",
                missing_value=_marker,
            )

        request = TestRequest()

        widget = FieldWidget(IWithText["text"], RichTextWidget(request))
        widget.update()

        converter = RichTextConverter(IWithText["text"], widget)

        # Test with None input.
        self.assertRaises(ValueError, converter.toFieldValue, None)
        self.assertTrue(converter.toWidgetValue(None) is None)

        # Test with string input.
        self.assertRaises(ValueError, converter.toFieldValue, b"")
        self.assertRaises(ValueError, converter.toFieldValue, b"Foo")
        self.assertRaises(ValueError, converter.toWidgetValue, b"")
        self.assertRaises(ValueError, converter.toWidgetValue, b"Foo")

        # Test with unicode input.
        self.assertTrue(converter.toFieldValue(u"") is _marker)
        self.assertEqual(converter.toFieldValue(u"Foo").raw, u"Foo")
        self.assertTrue(isinstance(converter.toFieldValue(u"Foo"), RichTextValue))
        self.assertEqual(converter.toWidgetValue(u"").raw, u"")
        self.assertEqual(converter.toWidgetValue(u"Foo").raw, u"Foo")

        # Test with RichTextValue input.
        self.assertTrue(converter.toFieldValue(RichTextValue(u"")) is _marker)
        rich_text = RichTextValue(u"Foo")
        self.assertEqual(converter.toFieldValue(rich_text), rich_text)
        self.assertEqual(converter.toFieldValue(rich_text).raw, u"Foo")
        self.assertEqual(converter.toWidgetValue(rich_text), rich_text)

    def testRichTextAreaWidgetConverter(self):
        from zope.interface import Interface
        from plone.app.textfield import RichText
        from zope.publisher.browser import TestRequest
        from plone.app.textfield.value import RichTextValue
        from plone.app.textfield.widget import RichTextWidget
        from plone.app.textfield.widget import RichTextAreaConverter
        from z3c.form.widget import FieldWidget

        _marker = object()

        class IWithText(Interface):

            text = RichText(
                title=u"Text",
                default_mime_type="text/structured",
                output_mime_type="text/html",
                missing_value=_marker,
            )

        request = TestRequest()

        widget = FieldWidget(IWithText["text"], RichTextWidget(request))
        widget.update()

        converter = RichTextAreaConverter(IWithText["text"], widget)

        # Test with None input.
        self.assertRaises(ValueError, converter.toFieldValue, None)
        self.assertTrue(converter.toWidgetValue(None) is None)

        # Test with string input.
        self.assertTrue(converter.toFieldValue("") is _marker)
        self.assertRaises(ValueError, converter.toFieldValue, b"Foo")
        self.assertRaises(ValueError, converter.toWidgetValue, b"")
        self.assertRaises(ValueError, converter.toWidgetValue, b"Foo")

        # Test with unicode input.
        self.assertTrue(converter.toFieldValue(u"") is _marker)
        self.assertEqual(converter.toFieldValue(u"Foo").raw, u"Foo")
        self.assertTrue(isinstance(converter.toFieldValue(u"Foo"), RichTextValue))
        self.assertEqual(converter.toWidgetValue(u""), u"")
        self.assertEqual(converter.toWidgetValue(u"Foo"), u"Foo")

        # Test with RichTextValue input.
        self.assertTrue(converter.toFieldValue(RichTextValue(u"")) is _marker)
        rich_text = RichTextValue(u"Foo")
        self.assertEqual(converter.toFieldValue(rich_text), rich_text)
        self.assertEqual(converter.toFieldValue(rich_text).raw, u"Foo")
        self.assertEqual(converter.toWidgetValue(rich_text), u"Foo")

    def testWidgetAllowedTypesDefault(self):
        from zope.interface import Interface, implementer
        from plone.app.textfield import RichText
        from zope.publisher.browser import TestRequest
        from Products.CMFCore.PortalContent import PortalContent
        from plone.app.textfield.widget import RichTextWidget
        from z3c.form.widget import FieldWidget

        class IWithText(Interface):

            text = RichText(
                title=u"Text",
                default_mime_type="text/structured",
                output_mime_type="text/html",
            )

        @implementer(IWithText)
        class Context(PortalContent):

            text = None

        request = TestRequest()

        widget = FieldWidget(IWithText["text"], RichTextWidget(request))
        widget.update()

        self.portal["portal_properties"]["site_properties"]._setPropValue(
            "forbidden_contenttypes", ["text/structured"]
        )

        allowed = widget.allowedMimeTypes()
        self.failUnless("text/html" in allowed)
        self.failIf("text/structured" in allowed)

    def testWidgetAllowedTypesField(self):
        from zope.interface import Interface, implementer
        from plone.app.textfield import RichText
        from zope.publisher.browser import TestRequest
        from Products.CMFCore.PortalContent import PortalContent
        from plone.app.textfield.widget import RichTextWidget
        from z3c.form.widget import FieldWidget

        class IWithText(Interface):

            text = RichText(
                title=u"Text",
                default_mime_type="text/structured",
                output_mime_type="text/html",
                allowed_mime_types=("text/structured", "text/html"),
            )

        @implementer(IWithText)
        class Context(PortalContent):

            text = None

        request = TestRequest()

        widget = FieldWidget(IWithText["text"], RichTextWidget(request))
        widget.update()

        self.portal["portal_properties"]["site_properties"]._setPropValue(
            "forbidden_contenttypes", ["text/structured"]
        )

        allowed = widget.allowedMimeTypes()
        self.failUnless("text/html" in allowed)
        self.failUnless("text/structured" in allowed)

    def test_getSize(self):
        from plone.app.textfield.value import RichTextValue

        value = RichTextValue(u"\u2603")
        self.assertEqual(3, value.getSize())


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if six.PY2:
            want = re.sub("b'(.*?)'", "'\\1'", want)
            want = re.sub(
                "zope.schema._bootstrapinterfaces.WrongType", "WrongType", want
            )
            want = re.sub("zope.interface.exceptions.Invalid", "Invalid", want)
            want = re.sub(
                "zope.schema._bootstrapinterfaces.ConstraintNotSatisfied",
                "ConstraintNotSatisfied",
                want,
            )
        else:
            want = re.sub("u'(.*?)'", "'\\1'", want)
            want = re.sub('u"(.*?)"', '"\\1"', want)

        return doctest.OutputChecker.check_output(self, want, got, optionflags)


class TestTextfield(unittest.TestCase):
    def test_getWysiwygEditor(self):
        from plone.app.textfield.utils import getWysiwygEditor
        editor = getWysiwygEditor(None, [], u"TinyMCE")
        self.assertEquals(editor, u"tinymce")
        editor = getWysiwygEditor(u"None", [], u"TinyMCE")
        self.assertEquals(editor, u"plaintexteditor")
        editor = getWysiwygEditor(u"TinyMCE", [u"TinyMCE", u"None"], u"TinyMCE")
        self.assertEquals(editor, u"tinymce")
        editor = getWysiwygEditor(u"CKeditor", [u"TinyMCE", u"None"], u"TinyMCE")
        self.assertEquals(editor, u"tinymce")
        editor = getWysiwygEditor(u"CKeditor", [u"TinyMCE", u"CKeditor", u"None"], u"TinyMCE")
        self.assertEquals(editor, u"ckeditor")


def test_suite():

    suite = unittest.makeSuite(TestIntegration)
    for doctestfile in ["field.rst", "handler.rst", "marshaler.rst"]:
        suite.addTest(
            layered(
                doctest.DocFileSuite(
                    doctestfile, optionflags=doctest.ELLIPSIS, checker=Py23DocChecker(),
                ),
                layer=testing.PLONE_FIXTURE,
            )
        )
    flags = \
        doctest.NORMALIZE_WHITESPACE | \
        doctest.ELLIPSIS | \
        doctest.IGNORE_EXCEPTION_DETAIL
    suite.addTest(layered(
        doctest.DocFileSuite("richtext_widget.rst", optionflags=flags),
        layer=testing.PLONE_INTEGRATION_TESTING))
    return suite
