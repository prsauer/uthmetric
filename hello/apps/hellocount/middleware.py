import re

from django.middleware.cache import UpdateCacheMiddleware


class SmartUpdateCacheMiddleware(UpdateCacheMiddleware):
    def process_request(self, request):
        cookies = request.META.get('HTTP_COOKIE', '')

        # Strip all non-Django cookies.
        new_cookies = []
        for cookie in re.split("\;\s*", cookies):
            key, value = cookie.split("=")
            if "=" not in cookie:
                continue
            if key.lower().strip() in ("csrftoken", "sessionid"):
                new_cookies.append("%s=%s" % (key, value))
        request.META['HTTP_COOKIE'] = "; ".join(new_cookies)