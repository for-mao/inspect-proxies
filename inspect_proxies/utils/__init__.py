from collections import namedtuple
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)

InspectResult = namedtuple('InspectResult',
                           ['url', 'proxy', 'response', 'error'])
