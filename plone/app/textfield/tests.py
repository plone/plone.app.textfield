import unittest
from zope.testing import doctest
import zope.component.testing

from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc

import plone.app.textfield

ptc.setupPloneSite()

class UnitTestLayer:
    
    @classmethod
    def testTearDown(cls):
        zope.component.testing.tearDown()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        from Products.Five import zcml
        from Products.Five import fiveconfigure
        
        fiveconfigure.debug_mode = True
        zcml.load_config('configure.zcml', package=plone.app.textfield)
        fiveconfigure.debug_mode = False

IntegrationLayer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])

class TestIntegration(ptc.PloneTestCase):
    
    layer = IntegrationLayer

    def testTransformPlain(self):
        from zope.interface import Interface
        from plone.app.textfield import RichText
        
        class IWithText(Interface):
            
            text = RichText(title=u"Text",
                            default_mime_type='text/plain',
                            output_mime_type='text/html')
        
        value = IWithText['text'].fromUnicode(u"Some **text**")
        self.assertEquals(u'<p>Some **text**</p>', value.output)
    
    def testTransformStructured(self):
        from zope.interface import Interface
        from plone.app.textfield import RichText
        
        class IWithText(Interface):
            
            text = RichText(title=u"Text",
                            default_mime_type='text/structured',
                            output_mime_type='text/html')
        
        value = IWithText['text'].fromUnicode(u"Some **text**")
        self.assertEquals(u'<p>Some <strong>text</strong></p>\n', value.output)
    
    def testTransformView(self):
        from zope.interface import Interface, implements
        from plone.app.textfield import RichText
        from Products.CMFCore.PortalContent import PortalContent
        
        class IWithText(Interface):
            
            text = RichText(title=u"Text",
                            default_mime_type='text/structured',
                            output_mime_type='text/html')
        
        class Context(PortalContent):
            implements(IWithText)
            
            id = 'context'
            text = None
        
        context = Context()
        context.text = IWithText['text'].fromUnicode(u"Some **text**")
        
        self.portal._setObject('context', context)
        context = self.portal['context']
        
        output = context.restrictedTraverse('@@text-transform/text')()
        self.assertEquals(u'<p>Some <strong>text</strong></p>', output.strip())
        
        output = context.restrictedTraverse('@@text-transform/text/text/plain')()
        self.assertEquals(u'Some text', output.strip())
    
    def testWidgetExtract(self):
        from zope.interface import Interface, implements
        from plone.app.textfield import RichText
        from zope.publisher.browser import TestRequest
        from Products.CMFCore.PortalContent import PortalContent
        from plone.app.textfield.widget import RichTextWidget
        from z3c.form.widget import FieldWidget
        from z3c.form.interfaces import NOVALUE
        
        class IWithText(Interface):
            
            text = RichText(title=u"Text",
                            default_mime_type='text/structured',
                            output_mime_type='text/html')
        
        class Context(PortalContent):
            implements(IWithText)
            
            text = None
        
        context = Context()
        request = TestRequest()
        
        widget = FieldWidget(IWithText['text'], RichTextWidget(request))
        widget.update()
        
        value = widget.extract()
        self.assertEquals(NOVALUE, value)
        
        request.form['%s' % widget.name] = u"Sample **text**"
        request.form['%s.mimeType' % widget.name] = 'text/structured'
        
        value = widget.extract()
        self.assertEquals(u"<p>Sample <strong>text</strong></p>", value.output.strip())
    
    def testWidgetAllowedTypesDefault(self):
        from zope.interface import Interface, implements
        from plone.app.textfield import RichText
        from zope.publisher.browser import TestRequest
        from Products.CMFCore.PortalContent import PortalContent
        from plone.app.textfield.widget import RichTextWidget
        from z3c.form.widget import FieldWidget
        
        class IWithText(Interface):
            
            text = RichText(title=u"Text",
                            default_mime_type='text/structured',
                            output_mime_type='text/html')
        
        class Context(PortalContent):
            implements(IWithText)
            
            text = None
        
        context = Context()
        request = TestRequest()
        
        widget = FieldWidget(IWithText['text'], RichTextWidget(request))
        widget.update()
        
        self.portal['portal_properties']['site_properties']._setPropValue('forbidden_contenttypes', ['text/structured'])
        
        allowed = widget.allowedMimeTypes()
        self.failUnless('text/html' in allowed)
        self.failIf('text/structured' in allowed)
    
    def testWidgetAllowedTypesField(self):
        from zope.interface import Interface, implements
        from plone.app.textfield import RichText
        from zope.publisher.browser import TestRequest
        from Products.CMFCore.PortalContent import PortalContent
        from plone.app.textfield.widget import RichTextWidget
        from z3c.form.widget import FieldWidget
        
        class IWithText(Interface):
            
            text = RichText(title=u"Text",
                            default_mime_type='text/structured',
                            output_mime_type='text/html',
                            allowed_mime_types=('text/structured', 'text/html'))
        
        class Context(PortalContent):
            implements(IWithText)
            
            text = None
        
        context = Context()
        request = TestRequest()
        
        widget = FieldWidget(IWithText['text'], RichTextWidget(request))
        widget.update()
        
        self.portal['portal_properties']['site_properties']._setPropValue('forbidden_contenttypes', ['text/structured'])
        
        allowed = widget.allowedMimeTypes()
        self.failUnless('text/html' in allowed)
        self.failUnless('text/structured' in allowed)
        
    
def test_suite():
    
    field = doctest.DocFileSuite('field.txt', optionflags=doctest.ELLIPSIS)
    field.layer = UnitTestLayer
    
    handler = doctest.DocFileSuite('handler.txt', optionflags=doctest.ELLIPSIS)
    handler.layer = UnitTestLayer
    
    marshaler = doctest.DocFileSuite('marshaler.txt', optionflags=doctest.ELLIPSIS)
    marshaler.layer = UnitTestLayer
    
    return unittest.TestSuite((
        field, handler, marshaler,
        unittest.makeSuite(TestIntegration),
        ))
