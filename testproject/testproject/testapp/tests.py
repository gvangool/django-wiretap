from django.test import TestCase

from wiretap.models import Tap, Message

class TestProjectCapture(TestCase):
    def test_hello_url(self):
        self.assertEqual(Tap.objects.count(), 0)
        self.assertEqual(Message.objects.count(), 0)
        self.client.get('/hello')
        self.assertEqual(Message.objects.count(), 0)
        self.client.get('/hello/')
        self.assertEqual(Message.objects.count(), 1)
        self.client.get('/hello/world')
        self.assertEqual(Message.objects.count(), 2)
