from unittest import TestCase

from inspect_proxies.utils import function as func
from json.decoder import JSONDecodeError


class TestParseRequestsProxy(TestCase):

    def setUp(self):
        self.func = func.parse_requests_proxy

    def tearDown(self):
        pass

    def test_require_auth(self):
        proxy = {'https': 'https://hello:world@127.0.0.1:8899'}
        expected = {'scheme': 'https', 'ip': '127.0.0.1', 'port': 8899,
                    'username': 'hello', 'password': 'world'}
        self.assertEqual(self.func(proxy), expected)

    def test_no_auth(self):
        proxy = {'http': 'http://127.0.0.1:18899'}
        expected = {'scheme': 'http', 'ip': '127.0.0.1', 'port': 18899,
                    'username': None, 'password': None}
        self.assertEqual(self.func(proxy), expected)

    def test_empty_input(self):
        proxy = {}
        expected = None
        self.assertEqual(self.func(proxy), expected)

    def test_error_input(self):
        error_proxies = [None, 'None', [None], {None}]
        for i in error_proxies:
            with self.assertRaises(AttributeError) as exc:
                self.func(i)


class TestCreateRequestsProxy(TestCase):

    def setUp(self):
        self.func = func.create_request_proxy

    def tearDown(self):
        pass

    def test_require_auth(self):
        proxy = {'scheme': 'https', 'ip': '127.0.0.1', 'port': 8899,
                 'username': 'hello', 'password': 'world'}
        expected = {'https': 'https://hello:world@127.0.0.1:8899'}
        self.assertEqual(self.func(proxy), expected)
        proxy = "{'scheme': 'https', 'ip': '127.0.0.1', 'port': 8899, " \
                "'username': 'hello', 'password': 'world'},"
        self.assertEqual(self.func(proxy), expected)

    def test_no_auth(self):
        proxy = {'scheme': 'http', 'ip': '127.0.0.1', 'port': 18899,
                 'username': None, 'password': None}
        expected = {'http': 'http://127.0.0.1:18899'}
        self.assertEqual(self.func(proxy), expected)
        proxy = "{'scheme': \"http\", 'ip': '127.0.0.1', " \
                "'port': 18899, 'username': null, 'password': null}"
        self.assertEqual(self.func(proxy), expected)

    def test_empty_input(self):
        proxy = {}
        expected = {}
        self.assertEqual(self.func(proxy), expected)

    def test_error_input(self):
        error_proxies = [None, 'None', [None], {None}]
        for i in error_proxies:
            with self.assertRaises((TypeError, JSONDecodeError)) as exc:
                self.func(i)



