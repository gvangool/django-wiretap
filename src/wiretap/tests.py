from django.core.exceptions import MiddlewareNotUsed
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from wiretap.middleware import WiretapMiddleware
from wiretap.models import Message, Tap
from wiretap.views import capture

class WiretapTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    @override_settings(DEBUG=True)
    def test_enabled_if_debugging(self):
        WiretapMiddleware()

    @override_settings(DEBUG=False)
    def test_disabled_if_not_debugging(self):
        with self.assertRaises(MiddlewareNotUsed):
            WiretapMiddleware()

    @override_settings(DEBUG=True)
    def test_no_taps(self):
        self.assertEqual(Tap.objects.count(), 0)
        WiretapMiddleware().process_request(self.request_factory.get('/'))
        self.assertEqual(Message.objects.count(), 0)

    @override_settings(DEBUG=True)
    def test_tap_match(self):
        Tap.objects.create(path_regex='/test')
        WiretapMiddleware().process_request(self.request_factory.get('/test'))
        self.assertEqual(Message.objects.count(), 1)

    @override_settings(DEBUG=True)
    def test_tap_mismatch(self):
        Tap.objects.create(path_regex='/test')
        WiretapMiddleware().process_request(self.request_factory.get('/real'))
        self.assertEqual(Message.objects.count(), 0)

    @override_settings(DEBUG=True)
    def test_view_with_debug(self):
        Tap.objects.create(path_regex='/test')
        capture(self.request_factory.get('/real'))
        self.assertEqual(Message.objects.count(), 1)

    @override_settings(DEBUG=False)
    def test_view_without_debug(self):
        Tap.objects.create(path_regex='/test')
        capture(self.request_factory.get('/real'))
        self.assertEqual(Message.objects.count(), 1)

    @override_settings(DEBUG=True, WIRETAP_XFF=False)
    def test_remote_addr(self):
        Tap.objects.create(path_regex='/test')
        WiretapMiddleware().process_request(self.request_factory.get('/test', HTTP_X_FORWARDED_FOR='10.10.10.10, 10.0.0.1'))
        self.assertEqual(Message.objects.count(), 1)
        msg = Message.objects.all()[0]
        self.assertEqual(msg.remote_addr, '127.0.0.1')

    @override_settings(DEBUG=True, WIRETAP_XFF=True)
    def test_xff_header(self):
        Tap.objects.create(path_regex='/test')
        WiretapMiddleware().process_request(self.request_factory.get('/test', HTTP_X_FORWARDED_FOR='10.10.10.10, 10.0.0.1'))
        self.assertEqual(Message.objects.count(), 1)
        msg = Message.objects.all()[0]
        self.assertEqual(msg.remote_addr, '10.10.10.10')
