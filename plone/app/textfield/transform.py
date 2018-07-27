# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.cache import Cache
from ZODB.POSException import ConflictError
from plone.app.linkintegrity.utils import getOutgoingLinks
from plone.app.textfield.interfaces import ITransformer
from plone.app.textfield.interfaces import TransformError
from zope.component.hooks import getSite
from zope.interface import implementer

import logging


LOG = logging.getLogger('plone.app.textfield')


@implementer(ITransformer)
class PortalTransformsTransformer(object):

    """Invoke portal_transforms to perform a conversion
    """

    def __init__(self, context):
        self.context = context

    def __call__(self, value, mimeType):
        # shortcut it we have no data
        if value.raw is None:
            return u''

        # shortcut if we already have the right value
        if mimeType is value.mimeType:
            return value.output

        site = getSite()

        transforms = getToolByName(site, 'portal_transforms', None)
        if transforms is None:
            raise TransformError("Cannot find portal_transforms tool")

        # check for changed scales for referenced images
        self.check_referenced_images(mimeType, value._raw_holder)

        try:
            data = transforms.convertTo(mimeType,
                                        value.raw_encoded,
                                        mimetype=value.mimeType,
                                        context=self.context,
                                        # portal_transforms caches on this
                                        object=value._raw_holder,
                                        encoding=value.encoding)
            if data is None:
                # TODO: i18n
                msg = (u'No transform path found from "%s" to "%s".' %
                       (value.mimeType, mimeType))
                LOG.error(msg)
                # TODO: memoize?
                # plone_utils = getToolByName(self.context, 'plone_utils')
                # plone_utils.addPortalMessage(msg, type='error')
                # FIXME: message not always rendered, or rendered later on
                # other page.
                # The following might work better, but how to get the request?
                # IStatusMessage(request).add(msg, type='error')
                return u''

            else:
                output = data.getData()
                return output.decode(value.encoding)
        except ConflictError:
            raise
        except Exception as e:
            # log the traceback of the original exception
            LOG.error("Transform exception", exc_info=True)
            raise TransformError('Error during transformation', e)

    def check_referenced_images(self, target_mimetype, cache_obj):
        # referenced image scale urls get outdated if the images are modified.
        # purging the transform cache updates those urls.
        cache = Cache(cache_obj, context=self.context)
        data = cache.getCache(target_mimetype)
        if data is None:
            # not cached ... return
            return
        # get the original save time from the cached data dict
        orig_time = getattr(cache_obj, cache._id).values()[0][0]
        # lookup referenced images and check modification time
        for ref_img in getOutgoingLinks(self.context):
            # XXX: not sure if it is a potential performance problem
            # looking up the image object
            if ref_img.to_object.modified() > orig_time:
                # found an updated image: purge the cache
                cache.purgeCache()
                return
