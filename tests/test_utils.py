import unittest
from json.decoder import JSONDecodeError
from unittest import TestCase

import requests

from inspect_proxies.utils import InspectResult
from inspect_proxies.utils import function as func


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


class TestOutputFormat(TestCase):

    def setUp(self):
        self.func = func.output_format
        self.data = InspectResult(
            url='http://httpbin.org/ip',
            proxy={'http': 'http://127.0.0.1:8899'},
            response=requests.get('http://httpbin.org/ip'),
            error=None
        )

    def tearDown(self):
        pass

    def testResultType(self):
        self.assertIsInstance(self.func(self.data), dict)

    def testResultKeys(self):
        result = self.func(self.data)
        for i in ['proxy', 'url', 'spend_time', 'status', 'exception']:
            self.assertIn(i, result.keys())

    def testResultValue(self):
        result = self.func(self.data)
        self.assertEqual('{"http": "http://127.0.0.1:8899"}', result['proxy'])
        self.assertEqual('http://httpbin.org/ip', result['url'])
        self.assertIsInstance(result['spend_time'], float)
        self.assertEqual(200, result['status'])
        self.assertEqual(None, result['exception'])


class TestOutputFormatViewProxy(TestCase):

    def setUp(self):
        self.func = func.output_format_view_proxy
        self.data = InspectResult(
            url='http://httpbin.org/ip',
            proxy={'http': 'http://127.0.0.1:8899'},
            response=requests.get('http://httpbin.org/ip'),
            error=None
        )

    def tearDown(self):
        pass

    def testResult(self):
        result = self.func(self.data)
        self.assertIsInstance(result, dict)
        for i in ['url', 'spend_time', 'status', 'exception',
                  'scheme', 'username', 'password', 'ip', 'port']:
            self.assertIn(i, result.keys())

        self.assertNotIn('proxy', result.keys())
        spend_time = result.pop('spend_time')
        self.assertIsInstance(spend_time, float)
        self.assertDictEqual(result, {
            'url': 'http://httpbin.org/ip',
            'status': 200,
            'exception': 'None',
            'scheme': 'http',
            'username': None,
            'password': None,
            'ip': '127.0.0.1',
            'port': 8899
        })


if __name__ == '__main__':
    unittest.main()
