from typing import Callable
from typing import Generator

from inspect_proxies.utils.function import create_request_proxy
from inspect_proxies.utils.function import file_storage


class Storage(object):

    def __init__(self,
                 parse: Callable=create_request_proxy,
                 generate_storage: Callable=file_storage,
                 **kwargs
                 ):
        self.parse = parse
        self.storage = generate_storage(**kwargs)

    def get_proxies(self) -> Generator:
        """
        :return: {'scheme':'scheme://domain or ip:port',}
        """
        for doc in self.storage:
            yield self.parse(doc)

