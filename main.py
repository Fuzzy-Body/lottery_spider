# coding: utf-8

import time
import json
import pickle
import requests

from log import logger
from consts import *


HEADER = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
}


def save(data, filename='data/match_list.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def load(filename='data/match_list.pkl'):
    with open(filename, 'r') as f:
        data = pickle.load(f)
    return data


def get_match_list():
    ts = int(time.time() * 1000)
    match_list_url = MATCH_LIST.format(ts=ts)
    response = requests.get(match_list_url, headers=HEADER)
    if response.status_code != 200:
        logger.error('get_match_list error, code: %s' % response.status_code)
        logger.error(response.text)
        raise
    data = response.text.replace('getMatchList', '')
    data = data.strip('();')
    data = json.loads(data)
    save(data)


if __name__ == '__main__':
    get_match_list()
    print(load())
