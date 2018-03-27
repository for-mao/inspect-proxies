from queue import Queue
from threading import Thread
from typing import Tuple

from requests.api import request

from inspect_proxies.output import Output
from inspect_proxies.utils import InspectResult


class ThreadProxyInspector(object):

    def __init__(self, storage, **kwargs):
        """
        :param storage:
        :param kwargs:
        """
        self.proxies = Queue()
        self.result = Queue()
        self.__threads = None
        self.thread_number = kwargs.get('thread_number', 20)
        self.url = kwargs.get('url', 'https://httpbin.org')
        self.requests_params = kwargs.get('requests_params', {})
        self.storage = storage
        self.storage_params = kwargs.get('storage_params')
        self.output_c = kwargs.get('output', Output)
        self.output_params = kwargs.get('output_params', {})
        self.output = None

    @property
    def threads(self) -> [Tuple, None]:
        return self.__threads

    def run(self):
        self.create_threads()
        self.load_proxies()
        self.await_task_done()
        self.output = self.output_c(self.result, **self.output_params)
        self.output.output()

    def thread_task(self):
        while True:
            proxy = self.proxies.get()
            try:
                resp = request(
                    self.requests_params.pop('method')
                    if 'method' in self.requests_params else 'get',
                    self.url, proxies=proxy, **self.requests_params)
            except Exception as exc:
                self.result.put(
                    InspectResult(
                        response=None, proxy=proxy, error=exc, url=self.url
                    ))
            else:
                self.result.put(
                    InspectResult(
                        response=resp, proxy=proxy, error=None, url=self.url
                    ))
            finally:
                self.proxies.task_done()

    def create_threads(self):
        _list = []
        for i in range(self.thread_number):
            t = Thread(
                target=self.thread_task,
                name='proxy_inspector_{}'.format(i),
            )
            t.setDaemon(True)
            t.start()
            _list.append(t)
        self.__threads = tuple(_list)

    def load_proxies(self):
        """
        from storage load proxy to self.proxies
        :return:
        """
        storage = self.storage(**self.storage_params)
        for proxy in storage.get_proxies():
            self.proxies.put(proxy)

    def await_task_done(self):
        self.proxies.join()
