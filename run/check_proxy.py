from inspect_proxies.inspector import ThreadProxyInspector
from inspect_proxies.output import Output
from inspect_proxies.storage import Storage
from inspect_proxies.utils.function import parse_file_proxy
from inspect_proxies.utils.function import mongodb_storage
from private_settings import MONGO_URI

params = {
    'thread_number': 50,  # default 20
    'url': 'https://httpbin.org/ip',  # default https://httpbin.org
    'requests_params': {
        'method': 'get',  # default get
        'timeout': 10,   # no default
        'allow_redirects': False,  # default True
        'headers': {},
    },
    'output': Output,  # class default Output
    'output_params': {
        # '_format': '',  # default dict
        # 'position': ''  # default console
    },  # your output instantiation required params
    'storage': Storage,  # required
    'storage_params': {
        'parse': parse_file_proxy,  # required
        'generate_storage': mongodb_storage,   # required
        'mongo_uri': MONGO_URI,  # callable of generate_storage required param
        'db': 'vps_management',
        'coll': 'service_shadowsocks',
    }
}

if __name__ == '__main__':
    inspector = ThreadProxyInspector(**params)
    inspector.run()
