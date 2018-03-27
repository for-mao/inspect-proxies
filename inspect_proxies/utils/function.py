from json import dumps
from json import loads
from typing import Dict
from typing import Generator

from pymongo.cursor import Cursor
from pymongo import MongoClient

from inspect_proxies.utils import InspectResult
from inspect_proxies.utils import pp


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


def output_position_console(doc: Dict):
    pp.pprint(doc)


def parse_file_proxy(line: [str, Dict]) -> Dict:
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
        print(parse_file_proxy(i))
