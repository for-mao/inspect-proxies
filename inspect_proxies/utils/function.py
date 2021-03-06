from json import dumps
from json import loads
from typing import Dict
from typing import Generator
from urllib.parse import urlparse

from pymongo.cursor import Cursor
from pymongo import MongoClient
from pymongo.collection import Collection

from inspect_proxies.utils import InspectResult
from inspect_proxies.utils import pp


def total_numbers(func):

    numbers = {'invalid': 0, 'valid': 0}

    def wrapper(doc, *args, **kwargs):
        if doc.get('exception') and doc.get('exception') != 'None':
            numbers['invalid'] += 1
        else:
            numbers['valid'] += 1

        res = func(doc, *args, **kwargs)
        print(numbers)

        return res

    return wrapper


def collect_invalid_ips(func):
    import datetime
    from os.path import abspath
    from os.path import dirname
    path = dirname(dirname(dirname(abspath(__file__))))
    with open('{}/invalid_ips.txt'.format(path), 'a') as f:
        f.write('\n\n\n{} invalid proxy\n'.format(datetime.datetime.today()))

    def wrapper(doc, *args, **kwargs):
        if doc.error and doc.error != 'None':
            proxy = parse_requests_proxy(doc.proxy)
            with open('{}/invalid_ips.txt'.format(path), 'a') as f:
                f.write('ip:{}  port:{}\n'.format(proxy['ip'], proxy['port']))

        res = func(doc, *args, **kwargs)

        return res

    return wrapper


def _parse_auth_uri(uri: str) -> Dict:
    if '@' in uri:
        split_res = uri.split('@')
        user, pwd = split_res[0].split(':')
        host, port = split_res[1].split(':')
    else:
        user, pwd = (None, None)
        host, port = uri.split(':')
    return {
        'username': user,
        'password': pwd,
        'ip': host,
        'port': int(port)
    }


def parse_requests_proxy(proxy: Dict) -> Dict:
    """
    :param proxy: {'http': 'http://...'}
    :return: Dict: keys include username, password, ip, port
    """
    for scheme, p in proxy.items():
        res = {'scheme': scheme}
        auth = urlparse(p).netloc
        res.update(_parse_auth_uri(auth))
        return res


def output_format_view_proxy(doc: InspectResult) -> Dict:
    """
    Handle result of output_format view proxy document
    :param doc:
    :return:
    """
    res = output_format(doc)
    del res['proxy']
    res['exception'] = str(res['exception'])
    res.update(parse_requests_proxy(doc.proxy))
    return res


@collect_invalid_ips
def output_format_filter_invalid_proxy(doc: InspectResult) -> Dict:
    """
    Handle result of output_format view proxy document
    :param doc:
    :return:
    """
    res = output_format(doc)
    if res['exception'] is None and res['status'] == 200:
        del res['proxy']
        del res['exception']
        res.update(parse_requests_proxy(doc.proxy))
        return res
    else:
        return dict()


def output_format(doc: InspectResult) -> Dict:
    """
    from once inspect result extract message
    :param doc: result of inspect proxy
    :return:
    """
    resp = doc.response
    if resp:
        seconds = resp.elapsed.total_seconds()
        status = resp.status_code
    else:
        seconds = None
        status = None
    return {
        'proxy': dumps(doc.proxy),
        'url': doc.url,
        'spend_time': seconds,
        'status': status,
        'exception': type(doc.error) if doc.error is not None else None
    }


@total_numbers
def output_position_console(doc: Dict):

    pp.pprint(doc)


def output_position_mongodb(doc: Dict, coll: Collection):
    if doc:
        coll.insert_one(doc)


def create_request_proxy(line: [str, Dict]) -> Dict:
    """
    :param line: dict or json
        {'ip': '', 'port': '', 'username': '', 'password':'', 'scheme': ''}
    :return: dict: {'scheme': 'proxy'}
    """
    if type(line) is str:
        line = loads(line.strip(',').replace("'", '"'))
    if type(line) is not dict:
        raise TypeError(
            "excepted type of line is dict, is not {}".format(type(line))
        )
    if not line:
        return {}
    if line.get('username'):
        return {
            line['scheme']: '{scheme}://{username}:{password}@'
                            '{ip}:{port}'.format(
                scheme=line['scheme'], username=line['username'],
                password=line['password'], ip=line.get('ip') or line['domain'],
                port=line.get('port', 80 if line['scheme'] == 'http' else 443)
            )
        }
    else:
        return {
            line['scheme']: '{scheme}://{ip}:{port}'.format(
                scheme=line['scheme'],
                ip=line.get('ip') or line['domain'],
                port=line.get('port', 80 if line['scheme'] == 'http' else 443)
            )
        }


def file_storage(path: str) -> Generator:
    """
    :param path: file path
    :return: line
    """
    with open(path) as f:
        for _ in f:
            line = _.strip()
            if line:
                yield line


def mongodb_storage(
        mongo_uri: str, db: str, coll: str, _filter: Dict={}
) -> Cursor:
    client = MongoClient(mongo_uri)
    coll = client[db][coll]
    return coll.find(_filter, no_cursor_timeout=False)


if __name__ == '__main__':
    storage = file_storage('../../tests/docs/proxies_demo.txt')
    for i in storage:
        print(create_request_proxy(i))
