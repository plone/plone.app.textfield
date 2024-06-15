from plone.app import testing
from plone.testing import layered

import doctest
import plone.app.textfield
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
        from plone.app.textfield import RichText
        from zope.interface import Interface

        class IWithText(Interface):
            text = RichText(
                title="Text",
                default_mime_type="text/plain",
                output_mime_type="text/html",
            )

        value = IWithText["text"].fromUnicode("Some **text**")
        self.assertEqual("<p>Some **text**</p>", value.output)

    def testTransformNone(self):
        from plone.app.textfield.value import RichTextValue

        value = RichTextValue()
        # Mostly, these calls simply should not give an error.
        self.assertEqual(None, value.raw)
        self.assertEqual(None, value.output)

    def testTransformStructured(self):
        from plone.app.textfield import RichText
        from zope.interface import Interface

        class IWithText(Interface):
            text = RichText(
                title="Text",
                default_mime_type="text/structured",
                output_mime_type="text/html",
            )

        value = IWithText["text"].fromUnicode("Some **text**")
        self.assertEqual("<p>Some <strong>text</strong></p>\n", value.output)

    def testTransformView(self):
        from plone.app.textfield import RichText
        from Products.CMFCore.PortalContent import PortalContent
        from zope.interface import implementer
        from zope.interface import Interface

        class IWithText(Interface):
            text = RichText(
                title="Text",
                default_mime_type="text/structured",
                output_mime_type="text/html",
            )

        @implementer(IWithText)
        class Context(PortalContent):
            id = "context"
            text = None

        context = Context()
        context.text = IWithText["text"].fromUnicode("Some **text**")

        self.portal._setObject("context", context)
        context = self.portal["context"]

        output = context.restrictedTraverse("@@text-transform/text")()
        self.assertEqual("<p>Some <strong>text</strong></p>", output.strip())

        output = context.restrictedTraverse("@@text-transform/text/text/plain")()
        self.assertEqual("Some text", output.strip())

        # test transform shortcircuit when input and output type is the
        # same. this used to cause infinite recursion
        class IWithText(Interface):
            text = RichText(
                title="Text",
                default_mime_type="text/html",
                output_mime_type="text/html",
            )

        context.text = IWithText["text"].fromUnicode("<span>Some html</span>")
        output = context.restrictedTraverse("@@text-transform/text")()
        self.assertEqual("<span>Some html</span>", output.strip())

    def testTransformNoneView(self):
        from plone.app.textfield import RichText
        from plone.app.textfield.value import RichTextValue
        from Products.CMFCore.PortalContent import PortalContent
        from zope.interface import implementer
        from zope.interface import Interface

        class IWithText(Interface):
            text = RichText(
                title="Text",
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
        self.assertEqual("", output.strip())

        output = context.restrictedTraverse("@@text-transform/text/text/plain")()
        self.assertEqual("", output.strip())

    def testWidgetExtract(self):
        from plone.app.textfield import RichText
        from plone.app.textfield.widget import RichTextWidget
        from Products.CMFCore.PortalContent import PortalContent
        from z3c.form.interfaces import NOVALUE
        from z3c.form.widget import FieldWidget
        from zope.interface import implementer
        from zope.interface import Interface
        from zope.publisher.browser import TestRequest

        class IWithText(Interface):
            text = RichText(
                title="Text",
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
        self.assertEqual(NOVALUE, value)

        request.form["%s" % widget.name] = "Sample **text**"
        request.form["%s.mimeType" % widget.name] = "text/structured"

        value = widget.extract()
        self.assertEqual("<p>Sample <strong>text</strong></p>", value.output.strip())

    def testRichTextWidgetConverter(self):
        from plone.app.textfield import RichText
        from plone.app.textfield.value import RichTextValue
        from plone.app.textfield.widget import RichTextConverter
        from plone.app.textfield.widget import RichTextWidget
        from z3c.form.widget import FieldWidget
        from zope.interface import Interface
        from zope.publisher.browser import TestRequest

        _marker = object()

        class IWithText(Interface):
            text = RichText(
                title="Text",
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
        self.assertTrue(converter.toFieldValue("") is _marker)
        self.assertEqual(converter.toFieldValue("Foo").raw, "Foo")
        self.assertTrue(isinstance(converter.toFieldValue("Foo"), RichTextValue))
        self.assertEqual(converter.toWidgetValue("").raw, "")
        self.assertEqual(converter.toWidgetValue("Foo").raw, "Foo")

        # Test with RichTextValue input.
        self.assertTrue(converter.toFieldValue(RichTextValue("")) is _marker)
        rich_text = RichTextValue("Foo")
        self.assertEqual(converter.toFieldValue(rich_text), rich_text)
        self.assertEqual(converter.toFieldValue(rich_text).raw, "Foo")
        self.assertEqual(converter.toWidgetValue(rich_text), rich_text)

    def testRichTextAreaWidgetConverter(self):
        from plone.app.textfield import RichText
        from plone.app.textfield.value import RichTextValue
        from plone.app.textfield.widget import RichTextAreaConverter
        from plone.app.textfield.widget import RichTextWidget
        from z3c.form.widget import FieldWidget
        from zope.interface import Interface
        from zope.publisher.browser import TestRequest

        _marker = object()

        class IWithText(Interface):
            text = RichText(
                title="Text",
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
        self.assertTrue(converter.toFieldValue("") is _marker)
        self.assertEqual(converter.toFieldValue("Foo").raw, "Foo")
        self.assertTrue(isinstance(converter.toFieldValue("Foo"), RichTextValue))
        self.assertEqual(converter.toWidgetValue(""), "")
        self.assertEqual(converter.toWidgetValue("Foo"), "Foo")

        # Test with RichTextValue input.
        self.assertTrue(converter.toFieldValue(RichTextValue("")) is _marker)
        rich_text = RichTextValue("Foo")
        self.assertEqual(converter.toFieldValue(rich_text), rich_text)
        self.assertEqual(converter.toFieldValue(rich_text).raw, "Foo")
        self.assertEqual(converter.toWidgetValue(rich_text), "Foo")

    def testWidgetAllowedTypesDefault(self):
        from plone.app.textfield import RichText
        from plone.app.textfield.widget import RichTextWidget
        from Products.CMFCore.PortalContent import PortalContent
        from z3c.form.widget import FieldWidget
        from zope.interface import implementer
        from zope.interface import Interface
        from zope.publisher.browser import TestRequest

        class IWithText(Interface):
            text = RichText(
                title="Text",
                default_mime_type="text/structured",
                output_mime_type="text/html",
            )

        @implementer(IWithText)
        class Context(PortalContent):
            text = None

        request = TestRequest()

        widget = FieldWidget(IWithText["text"], RichTextWidget(request))
        widget.update()

        allowed = widget.allowedMimeTypes()
        self.assertTrue("text/html" in allowed)
        self.assertFalse("text/structured" in allowed)

    def testWidgetAllowedTypesField(self):
        from plone.app.textfield import RichText
        from plone.app.textfield.widget import RichTextWidget
        from Products.CMFCore.PortalContent import PortalContent
        from z3c.form.widget import FieldWidget
        from zope.interface import implementer
        from zope.interface import Interface
        from zope.publisher.browser import TestRequest

        class IWithText(Interface):
            text = RichText(
                title="Text",
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

        allowed = widget.allowedMimeTypes()
        self.assertTrue("text/html" in allowed)
        self.assertTrue("text/structured" in allowed)

    def test_getSize(self):
        from plone.app.textfield.value import RichTextValue

        value = RichTextValue("\u2603")
        self.assertEqual(3, value.getSize())


class TestTextfield(unittest.TestCase):
    def test_getWysiwygEditor(self):
        from plone.app.textfield.utils import getWysiwygEditor

        editor = getWysiwygEditor(None, [], "TinyMCE")
        self.assertEqual(editor, "tinymce")
        editor = getWysiwygEditor("None", [], "TinyMCE")
        self.assertEqual(editor, "plaintexteditor")
        editor = getWysiwygEditor("TinyMCE", ["TinyMCE", "None"], "TinyMCE")
        self.assertEqual(editor, "tinymce")
        editor = getWysiwygEditor("CKeditor", ["TinyMCE", "None"], "TinyMCE")
        self.assertEqual(editor, "tinymce")
        editor = getWysiwygEditor(
            "CKeditor", ["TinyMCE", "CKeditor", "None"], "TinyMCE"
        )
        self.assertEqual(editor, "ckeditor")


def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestIntegration)
    for doctestfile in ["field.rst", "handler.rst", "marshaler.rst"]:
        suite.addTest(
            layered(
                doctest.DocFileSuite(
                    doctestfile,
                    optionflags=doctest.ELLIPSIS,
                ),
                layer=testing.PLONE_FIXTURE,
            )
        )
    flags = (
        doctest.NORMALIZE_WHITESPACE
        | doctest.ELLIPSIS
        | doctest.IGNORE_EXCEPTION_DETAIL
    )
    suite.addTest(
        layered(
            doctest.DocFileSuite("richtext_widget.rst", optionflags=flags),
            layer=testing.PLONE_INTEGRATION_TESTING,
        )
    )
    return suite
