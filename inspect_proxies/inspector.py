from queue import Queue
from threading import Thread
from threading import current_thread
from typing import Tuple

from requests.api import request

from inspect_proxies.output import Output
from inspect_proxies.utils import InspectResult
from inspect_proxies.utils.logs import create_logger
from inspect_proxies.utils.logs import root_logger

logger = create_logger(__name__)


class ThreadProxyInspector(object):

    def __init__(self, storage, **kwargs):
        """
        :param storage:
        :param kwargs:
        """
        root_logger.setLevel(kwargs.get('log_level', root_logger.level))
        self.proxies = Queue()
        self.result = Queue()
        self.__threads = None
        self.thread_number = kwargs.get('thread_number', 20)
        self.url = kwargs.get('url', 'www.httpbin.org/ip')
        self.requests_params = kwargs.get('requests_params', {})
        self.storage = storage
        self.storage_params = kwargs.get('storage_params')
        self.output_c = kwargs.get('output', Output)
        self.output_params = kwargs.get('output_params', {})
        self.output = None
        self.print_msg()

    def print_msg(self):
        logger.info(
            'Start to inspect proxies '
            'with multiple threads[{}]'.format(self.thread_number)
        )
        logger.info('Await inspect url>>>{}'.format(self.url))

    @property
    def threads(self) -> [Tuple, None]:
        return self.__threads

    def run(self):
        self.create_threads()
        self.load_proxies()
        self.output = self.output_c(self.result, **self.output_params)
        logger.info('The environment initialization is complete')
        self.await_task_done()
        logger.info('output result with {}'.format(self.output_c.__name__))
        self.output.output()

    def thread_task(self):
        while True:
            proxy = self.proxies.get()
            params = self.requests_params.copy()
            try:
                url = "{scheme}://{url}".format(
                    scheme=next(iter(proxy.keys())),
                    url=self.url
                )
                resp = request(
                    params.pop('method', 'get'),
                    url, proxies=proxy, **params)
            except Exception as exc:
                res = InspectResult(
                    response=None, proxy=proxy, error=exc, url=self.url)
            else:
                res = InspectResult(
                    response=resp, proxy=proxy, error=None, url=self.url
                )
            finally:
                logger.debug('[{name}] inspect proxy {proxy} ({result})'.format(
                    name=current_thread().name,
                    proxy=next(iter(proxy.values())),
                    result=res.response or res.error
                ))
                self.result.put(res)
                self.proxies.task_done()

    def create_threads(self):
        logger.debug('Start to create threads')
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
        logger.debug('Start to load proxies from {}'.format(
            self.storage.__name__))
        storage = self.storage(**self.storage_params)
        count = 0
        for proxy in storage.get_proxies():
            count += 1
            self.proxies.put(proxy)
        logger.info('Successfully load {} proxies'.format(count))

    def await_task_done(self):
        logger.info('Wait for all inspection tasks to be completed.')
        self.proxies.join()
