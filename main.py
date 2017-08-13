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


def _request(url, to_replace='', **kwargs):
    ts = int(time.time() * 1000)
    url = url.format(ts=ts, **kwargs)
    logger.info('get url: %s' % url)
    response = requests.get(url, headers=HEADER)
    if response.status_code != 200:
        logger.error('get url %s error, code: %s' % (url, response.status_code))
        logger.error(response.text)
        raise
    data = response.text.replace(to_replace, '')
    data = data.strip('();')
    data = json.loads(data)
    return data


def get_match_list():
    data = _request(MATCH_LIST, to_replace='getMatchList')
    save(data)


def get_match_info(mid):
    # 获取比赛时间
    data = _request(MATCH_INFO, to_replace='getMatchInfo', mid=mid)

    return data['result']['date_cn'] + ' ' + data['result']['time_cn']


def get_asian_match(mid):
    # 获取亚盘澳门的信息
    data = _request(ASIAN_MATCH, to_replace='get_match_asia', mid=mid)
    for item in data['result']:
        if item['id'] == MACAO_ID:
            return {
                'home': item['h'],
                'drew': item['d'],
                'away': item['a'],
            }
    raise ValueError('没有找到澳门盘口')


def test():
    # get_match_list()
    # print(load())
    # print(get_match_info('96746'))
    print(get_asian_match('96746'))


if __name__ == '__main__':
    test()
