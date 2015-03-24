from django.http import HttpResponse

from wiretap.utils import store_request, WiretapHttpResponse

def capture(request):
    store_request(request)
    return WiretapHttpResponse(
        request,
        HttpResponse('200 OK', status=200, content_type="text/plain"),
        request.wiretap_message
    )
