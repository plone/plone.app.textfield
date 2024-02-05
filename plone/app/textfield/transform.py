from plone.app.textfield.interfaces import ITransformer
from plone.app.textfield.interfaces import TransformError
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.cache import Cache
from ZODB.POSException import ConflictError
from zope.component.hooks import getSite
from zope.interface import implementer

import logging
import re


LOG = logging.getLogger("plone.app.textfield")
imguid_re = re.compile(r'src="[^/]*/resolve[uU]id/([^/"]*)')


@implementer(ITransformer)
class PortalTransformsTransformer:
    """Invoke portal_transforms to perform a conversion"""

    _ccounter_id = "_v_catalog_counter"

    def __init__(self, context):
        self.context = context
        self.catalog = getToolByName(getSite(), "portal_catalog")

    def __call__(self, value, mimeType):
        # shortcut it we have no data
        if value.raw is None:
            return ""

        # shortcut if we already have the right value
        if mimeType is value.mimeType:
            return value.output

        site = getSite()

        transforms = getToolByName(site, "portal_transforms", None)
        if transforms is None:
            raise TransformError("Cannot find portal_transforms tool")

        # in Python 3 we pass text
        source_value = value.raw

        # check for modified referenced images
        self.check_referenced_images(source_value, mimeType, value._raw_holder)

        try:
            data = transforms.convertTo(
                mimeType,
                source_value,
                mimetype=value.mimeType,
                context=self.context,
                # portal_transforms caches on this
                object=value._raw_holder,
                encoding=value.encoding,
            )
            if data is None:
                # TODO: i18n
                msg = 'No transform path found from "{}" to "{}".'.format(
                    value.mimeType,
                    mimeType,
                )
                LOG.error(msg)
                # TODO: memoize?
                # plone_utils = getToolByName(self.context, 'plone_utils')
                # plone_utils.addPortalMessage(msg, type='error')
                # FIXME: message not always rendered, or rendered later on
                # other page.
                # The following might work better, but how to get the request?
                # IStatusMessage(request).add(msg, type='error')
                return ""

            return data.getData()
        except ConflictError:
            raise
        except Exception as e:
            # log the traceback of the original exception
            LOG.error("Transform exception", exc_info=True)
            raise TransformError("Error during transformation", e)

    def check_referenced_images(self, value, target_mimetype, cache_obj):
        # check catalog counter for changes first.
        counter = self.catalog.getCounter()
        cached_counter = getattr(cache_obj, self._ccounter_id, -1)
        if cached_counter == counter:
            # no changes made since last visit
            return
        # safe counter state
        setattr(cache_obj, self._ccounter_id, counter)

        # extract all image src uuids
        uids = imguid_re.findall(value)
        if len(uids) == 0:
            # no uuid here at all
            return

        # referenced image scale urls get outdated if the images are modified.
        # purging the transform cache updates those urls.
        cache = Cache(cache_obj, context=self.context)
        data = cache.getCache(target_mimetype)
        if data is None:
            # data is not cached
            return

        # get the original save time from the cached data dict
        cached_values = list(getattr(cache_obj, cache._id, {}).values())
        modified_imgs = []
        if len(cached_values):
            orig_time = cached_values[0][0]
            modified_imgs = self.catalog(
                UID=uids, modified=dict(query=orig_time, range="min")
            )

        if len(modified_imgs) > 0:
            cache.purgeCache()
