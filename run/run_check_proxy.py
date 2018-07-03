from random import choice
from inspect_proxies.inspector import ThreadProxyInspector
from inspect_proxies.output import Output
from inspect_proxies.storage import Storage
from inspect_proxies.utils.function import create_request_proxy
from inspect_proxies.utils.function import mongodb_storage
from inspect_proxies.utils.function import output_format_view_proxy
from inspect_proxies.utils.function import output_position_mongodb
from private_settings import MONGO_URI
from private_settings import URLS
from logging import DEBUG
from settings import HEADERS
from settings import USER_AGENTS
from pymongo import MongoClient

client = MongoClient(MONGO_URI)

params = {
    'log_level': DEBUG,
    'thread_number': 50,  # default 20
    # 'url': choice(URLS),  # default https://httpbin.org
    # 'url': 'https://www.linkedin.com',
    # 'url': 'https://www.linkedin.com',
    'requests_params': {
        'method': 'get',  # default get
        'timeout': 10,   # no default
        'allow_redirects': False,  # default True
        'headers': HEADERS.update({'User-Agent': choice(USER_AGENTS)}),
    },
    'output': Output,  # class default Output
    'output_params': {
        # '_format': output_format_view_proxy,  # default dict
        # 'position': output_position_mongodb,  # default console
        # 'coll': client['vps_management']['service_hoovers_inspect_res']
    },  # your output instantiation required params
    'storage': Storage,  # required
    'storage_params': {
        'parse': create_request_proxy,  # required
        'generate_storage': mongodb_storage,   # required
        'mongo_uri': MONGO_URI,  # callable of generate_storage required param
        'db': 'vps_management',
        'coll': 'service_new_email_shadowsocks',
        '_filter': {'scheme': 'https'}
    }
}

if __name__ == '__main__':
    inspector = ThreadProxyInspector(**params)
    inspector.run()
