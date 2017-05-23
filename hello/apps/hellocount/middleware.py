import re

from django.middleware.cache import UpdateCacheMiddleware


class SmartUpdateCacheMiddleware(UpdateCacheMiddleware):
    def process_request(self, request):
        cookie = self.STRIP_RE.sub('', request.META.get('HTTP_COOKIE', ''))   
        request.META['HTTP_COOKIE'] = cookie