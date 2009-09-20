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

    def afterSetUp(self):
        if hasattr(self.portal, '_v_transform_cache'):
            del self.portal._v_transform_cache

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

def test_suite():
    
    field = doctest.DocFileSuite('field.txt', optionflags=doctest.ELLIPSIS)
    field.layer = UnitTestLayer
    
    handler = doctest.DocFileSuite('handler.txt', optionflags=doctest.ELLIPSIS)
    handler.layer = UnitTestLayer
    
    return unittest.TestSuite((
        field, handler,
        unittest.makeSuite(TestIntegration),
        ))
