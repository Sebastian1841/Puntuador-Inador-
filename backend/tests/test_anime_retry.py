import unittest
from unittest.mock import patch
import httpx
from app.anime_catalog import request


class AnimeRetryTests(unittest.TestCase):
    @patch('app.anime_catalog.time.sleep')
    def test_transient_failure_recovers(self, sleep):
        statuses = iter([502, 429, 200])
        with httpx.Client(transport=httpx.MockTransport(
            lambda req: httpx.Response(next(statuses), json={'data': []})
        )) as client:
            self.assertEqual(request(client, 'anime'), {'data': []})

    @patch('app.anime_catalog.time.sleep')
    def test_permanent_failure_is_not_retried(self, sleep):
        calls = []
        def provider(req):
            calls.append(req)
            return httpx.Response(404)
        with httpx.Client(transport=httpx.MockTransport(provider)) as client:
            with self.assertRaises(httpx.HTTPStatusError):
                request(client, 'anime')
        self.assertEqual(len(calls), 1)

    @patch('app.anime_catalog.time.sleep')
    def test_timeout_stops_after_three_attempts(self, sleep):
        calls = []
        def provider(req):
            calls.append(req)
            raise httpx.ReadTimeout('Provider timed out', request=req)
        with httpx.Client(transport=httpx.MockTransport(provider)) as client:
            with self.assertRaises(httpx.ReadTimeout):
                request(client, 'anime')
        self.assertEqual(len(calls), 3)
