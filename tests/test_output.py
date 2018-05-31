import unittest
from unittest import TestCase
from queue import Queue

import requests

from inspect_proxies.output import Output
from inspect_proxies.utils import InspectResult


class OutPut(TestCase):

    def setUp(self):
        data = Queue()
        self.result = InspectResult(
            url='http://httpbin.org/ip',
            proxy={'http': 'http://127.0.0.1:8899'},
            response=requests.get('http://httpbin.org/ip'),
            error=None)
        self.position_data = []
        data.put(self.result)
        self.output = Output(
            data, position=lambda x:
            self.position_data.append({'position': True, 'data': x})
        )

    def tearDown(self):
        pass

    def test_start_status(self):
        self.assertEqual(self.output.data.empty(), False)

    def test_output(self):
        self.output.output()
        for i in self.position_data:
            self.assertEqual(i['position'], True)
            self.assertEqual(
                i['data'], self.output.format(self.result, **self.output.kwargs)
            )
        self.assertEqual(self.output.data.empty(), True)


if __name__ == '__main__':
    unittest.main()
