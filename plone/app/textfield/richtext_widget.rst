==============
RichTextWidget
==============

The widget can render a rich text field for a text:

  >>> from zope.interface.verify import verifyClass
  >>> from z3c.form import interfaces
  >>> from plone.app.textfield.widget import RichTextWidget

The ``RichTextWidget`` is a widget:

  >>> verifyClass(interfaces.IWidget, RichTextWidget)
  True

The widget can render a input field only by adapting a request:

  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> request.form['text'] = "<p>Hello world</p>"
  >>> request.form['text.mimetype'] = "text/html"
  >>> widget = RichTextWidget(request)
  >>> widget.context = layer['portal']
  >>> widget.name = 'text'
  >>> from plone.app.textfield import RichText
  >>> widget.field = RichText(allowed_mime_types=['text/html'])

Such a widget provides IWidget:

  >>> interfaces.IWidget.providedBy(widget)
  True

We also need to register the template for at least the widget and request:

  >>> import os.path
  >>> import zope.interface
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> import plone.app.textfield
  >>> import z3c.form.widget
  >>> template = os.path.join(os.path.dirname(plone.app.textfield.__file__),
  ...     'widget_input.pt')
  >>> factory = z3c.form.widget.WidgetTemplateFactory(template)
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='input')

If we render the widget we get the HTML:
  >>> widget.update()
  >>> print(widget.render())
  <div xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" class="richTextWidget" >
  ...<input type="hidden" id="text_text_format" name="text.mimeType" value="text/html" />
  ...<div>
  ...<textarea name="text" rows="25" class="pat-tinymce" id="text">&lt;p&gt;Hello world&lt;/p&gt;</textarea>
  ...</div>
  ...</div>

  >>> from zope.component import getGlobalSiteManager
  >>> gsm = getGlobalSiteManager()
  >>> gsm.unregisterAdapter(factory,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, None, None, None),
  ...     IPageTemplate, name='input')
  True
