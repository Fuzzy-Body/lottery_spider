# coding: utf-8

import time
import json
import xlwt
import pickle
import datetime
import requests

from log import logger
from consts import *


HEADER = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
}
# 超过十分钟就从头开始抓取
INTERNAL = 10 * 60
SLEEP = 2
MATCH_DATA = 'data/match_list.pkl'
RESUME_DATA = 'data/resume.pkl'
RESULT_TMP = 'data/result_tmp.pkl'
RESULT = 'data/result.pkl'


def save(data, filename=MATCH_DATA):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def load(filename=MATCH_DATA):
    try:
        f = open(filename, 'r')
        data = pickle.load(f)
    except IOError, KeyError:
        return None
    f.close()
    return data


def _request(url, to_replace='', **kwargs):
    ts = int(time.time() * 1000)
    url = url.format(ts=ts, **kwargs)
    logger.info('get url: %s' % url)
    response = requests.get(url, headers=HEADER)
    time.sleep(0.5)
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
    save(data['result'])
    return data['result']


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
    logger.error('%s没有找到澳门的盘口' % mid)
    return {
        'home': '--',
        'drew': '--',
        'away': '--',
    }


def get_odds(mid):
    # 获取固定奖金
    data = _request(ODD, to_replace='get_sporttery_odds', mid=mid)
    newest = data['result']['had']['list'][-1]
    return {
        'home': newest['h'],
        'drew': newest['d'],
        'away': newest['a'],
    }


def get_odds_bid(mid):
    # 获取威廉希尔的即时奖金, 有可能会没有
    url = ODDS_BID
    data = _request(ODDS_BID, to_replace='get_bid_odds', mid=mid)
    if data['status']['code'] != 0:
        logger.error('%s没有找到威廉希尔的盘口' % mid)
        return {
            'home': '--',
            'drew': '--',
            'away': '--',
            'all_home': '--',
            'all_drew': '--',
            'all_away': '--',
        }
    current = data['result']['current']
    result = {
        'home': current['h'],
        'drew': current['d'],
        'away': current['a'],
    }
    all_result = get_odds_bid_data(result['home'], result['drew'], result['away'])
    result.update(all_result)
    return result


def get_odds_bid_data(home, drew, away):
    # 获取威廉希尔的即时奖金, 有可能会没有
    url = ODDS_BID_DATA.format(home=home, drew=drew, away=away)
    url = url % '{ts}'
    data = _request(url, to_replace='deal_bid_current_all')
    if data['status']['code'] != 0:
        logger.error('%s没有找到威廉希尔的盘口' % mid)
        return {
            'all_home': '--',
            'all_drew': '--',
            'all_away': '--',
        }
    stat = data['result']['stat']
    return {
        'all_home': stat['h'],
        'all_drew': stat['d'],
        'all_away': stat['a'],
    }


def save_excel(data):
    logger.info('save excel start')
    f = xlwt.Workbook()
    sheet1 = f.add_sheet(u"博彩数据", cell_overwrite_ok=True)
    head = [u'ID', u'赛事编号', u'联赛', u'主队', u'客队', u'比赛开始时间', u'澳门-主',
            u'平', u'客', u'威廉希尔指数-主', u'平', u'客', u'威廉希尔总计-主', u'平', u'客',
            u'固定奖金-主', u'平', u'客']
    for item in range(len(head)):
        sheet1.write(0, item, head[item])
    row = 1
    for item in data:
        sheet1.write(row, 0, item['id'])
        sheet1.write(row, 1, item['num'])
        sheet1.write(row, 2, item['league_cn'])
        sheet1.write(row, 3, item['home_cn'])
        sheet1.write(row, 4, item['away_cn'])
        sheet1.write(row, 5, item['match_time'])
        sheet1.write(row, 6, item['macao_info']['home'])
        sheet1.write(row, 7, item['macao_info']['drew'])
        sheet1.write(row, 8, item['macao_info']['away'])
        sheet1.write(row, 9, item['willian_info']['home'])
        sheet1.write(row, 10, item['willian_info']['drew'])
        sheet1.write(row, 11, item['willian_info']['away'])
        sheet1.write(row, 12, item['willian_info']['all_home'])
        sheet1.write(row, 13, item['willian_info']['all_drew'])
        sheet1.write(row, 14, item['willian_info']['all_away'])
        sheet1.write(row, 15, item['odd']['home'])
        sheet1.write(row, 16, item['odd']['drew'])
        sheet1.write(row, 17, item['odd']['away'])
        row += 1
    today = datetime.datetime.now().strftime('%y-%m-%d-%H%M')
    filename = u'data/data-%s.xls' % today
    f.save(filename)
    logger.info('save excel done')


def resume():
    last_stop = load(RESUME_DATA)
    if not (last_stop and int(time.time()) - last_stop['ts'] < INTERNAL):
        logger.info('scawl form start')
        return {
            'match_list': get_match_list(),
            'result': [],
            'idx': 0
        }
    match_list = load(MATCH_DATA)
    result_tmp = load(RESULT_TMP)
    logger.info('last scawl %s' % last_stop['idx'])
    return {
        'match_list': match_list,
        'result': result_tmp,
        'idx': last_stop['idx'] + 1,
    }


def main():
    resume_info = resume()
    match_list = resume_info['match_list']
    result = resume_info['result']
    idx = resume_info['idx']
    logger.info('scrawl start')
    for match in match_list[idx:]:
        logger.info('scawling %s' % idx)
        match_id = match['id']
        item = {
            'id': match_id,
            'num': match['num'],
            'league_cn': match['l_cn'],
            'home_cn': match['h_cn'],
            'away_cn': match['a_cn'],
        }
        item['match_time'] = get_match_info(match_id)
        macao_info = get_asian_match(match_id)
        item['macao_info'] = macao_info
        odd = get_odds(match_id)
        item['odd'] = odd
        item['willian_info'] = get_odds_bid(match_id)
        result.append(item)
        save(result, RESULT_TMP)
        save({'idx': idx, 'ts': int(time.time())}, RESUME_DATA)
        if idx % 10 == 9:
            time.sleep(10)
        else:
            time.sleep(SLEEP)
        idx += 1
    save(result, RESULT)
    logger.info('scrawl done')
    save_excel(result)


def test():
    # get_match_list()
    # print(load())
    # print(get_match_info('96746'))
    # print(get_asian_match('96746'))
    # print(get_odds('96746'))
    print(get_odds_bid('96746'))

    # test excel
    # data = load(RESULT)
    # save_excel(data)


if __name__ == '__main__':
    main()
