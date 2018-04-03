from queue import Queue
from typing import Callable

from inspect_proxies.utils.function import output_format
from inspect_proxies.utils.function import output_position_console


class Output(object):

    def __init__(
            self, data: Queue,
            _format: Callable=output_format,
            position: Callable=output_position_console,
            **kwargs
    ):
        self.data = data
        self.format = _format
        self.position = position
        self.kwargs = kwargs

    def output(self):
        while not self.data.empty():
            self.position(self.format(self.data.get()), **self.kwargs)


