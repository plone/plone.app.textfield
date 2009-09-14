import unittest
from zope.testing import doctest
import zope.component.testing

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('field.txt', optionflags=doctest.ELLIPSIS, tearDown=zope.component.testing.tearDown),
        doctest.DocFileSuite('handler.txt', optionflags=doctest.ELLIPSIS, tearDown=zope.component.testing.tearDown),
        # doctest.DocFileSuite('transform.txt', optionflags=doctest.ELLIPSIS, tearDown=zope.component.testing.tearDown),
        ))
