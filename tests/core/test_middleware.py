from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase, override_settings

from cravensworth.core.middleware import cravensworth_middleware


@override_settings(CRAVENSWORTH={'TRACKING_COOKIE': 'tk'})
class TestCravensworthMiddleware(TestCase):
    client = Client()
    factory = RequestFactory()

    def test_sets_tracking_key(self):
        with patch(
            'cravensworth.core.utils.generate_tracking_key'
        ) as mock_generate_tracking_key:
            mock_generate_tracking_key.return_value = 'NEW_TRACKING_KEY'
            response = self.client.get('/')
        self.assertTrue('tk' in response.cookies)

        cookie = response.cookies['tk']
        self.assertEqual(cookie.value, 'NEW_TRACKING_KEY')
        self.assertEqual(cookie['max-age'], timedelta(days=365).total_seconds())
        self.assertEqual(cookie['path'], '/')
        self.assertEqual(cookie['httponly'], True)
        self.assertEqual(cookie['samesite'], 'Lax')

    def test_uses_existing_tracking_key(self):
        self.client.cookies.load({'tk': 'THE_TRACKING_KEY'})
        response = self.client.get('/')
        self.assertTrue('tk' in response.cookies)
        self.assertEqual(response.cookies['tk'].value, 'THE_TRACKING_KEY')

    def test_sets_state(self):
        middleware = cravensworth_middleware(lambda r: HttpResponse('OK'))
        request = self.factory.get('/')
        request.user = AnonymousUser()
        middleware(request)
        state = request._cravensworth_state
        self.assertIsNotNone(state)
