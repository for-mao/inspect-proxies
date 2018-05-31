import unittest
from unittest import TestCase

from inspect_proxies.storage import Storage


def generate_storage():
    yield {'scheme': 'https', 'ip': '127.0.0.1', 'port': 8899,
           'username': 'hello', 'password': 'world'}


class StorageCase(TestCase):

    def setUp(self):
        self.storage = Storage(generate_storage=generate_storage)
        self.expected = {'https': 'https://hello:world@127.0.0.1:8899'}

    def tearDown(self):
        pass
    
    def test_storage(self):
        for i in self.storage.get_proxies():
            self.assertDictEqual(i, self.expected)


if __name__ == '__main__':
    unittest.main()
