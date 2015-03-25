import re

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed

from wiretap.models import Tap
from wiretap.utils import store_request, WiretapHttpResponse

class WiretapMiddleware(object):
    """
    Wiretap middleware. Saves HTTP requests & responses to the `Message` model.
    """

    def __init__(self):
        """
        Initialise the middleware.
        """

        # Wiretap streams responses to disk, then stores the data in a
        # `FileField`.
        #
        # This isn't particularly performant, so we'll disable ourselves if
        # Django isn't in debug mode.
        if not getattr(settings, 'DEBUG', False):
            raise MiddlewareNotUsed()

    def should_tap(self, request):
        """
        Returns true if we should store the request/response.
        """

        matching_tap = False
        for tap in Tap.objects.all():
            if re.search(tap.path_regex, request.path):
                return True

        return False

    def process_request(self, request):
        """
        Process incoming requests. If we're tracking this request, we'll store
        a created `Message` object in `request.wiretap_message`.
        """

        request.wiretap_message = None

        if not self.should_tap(request):
            return

        store_request(request, sender=self.__class__)

    def process_response(self, request, response):
        """
        Process the response. If we're tracking this request,
        `request.wiretap_message` will be set.
        """

        if not request.wiretap_message:
            return response
        else:
            return WiretapHttpResponse(
                request,
                response,
                request.wiretap_message
            )
