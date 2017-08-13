# coding: utf-8

MATCH_LIST = 'http://i.sporttery.cn/api/fb_match_info/get_matches?f_callback=getMatchList&_={ts}'

MATCH_INFO = 'http://i.sporttery.cn/api/fb_match_info/get_match_info?mid={mid}'\
    '&f_callback=getMatchInfo&_={ts}'

# Asian Handicap 亚盘
ASIAN_MATCH = 'http://i.sporttery.cn/api/fb_match_info/get_asia/?f_callback=get_match_asia'\
    '&mid={mid}&_={ts}'
MACAO_ID = '229'

# 固定奖金
ODD = 'http://i.sporttery.cn/api/fb_match_info/get_odds/?f_callback=get_sporttery_odds'\
    '&mid={mid}&_={ts}'

# 威廉希尔的盘口, bid=42
ODDS_BID = 'http://i.sporttery.cn/api/fb_match_info/get_odds_bid/?f_callback=get_bid_odds'\
    '&bid=42&pool=three&mid={mid}&_={ts}'

# 威廉希尔的盘口数据
ODDS_BID_DATA = 'http://i.sporttery.cn/api/fb_match_info/get_bid_data/'\
    '?f_callback=deal_bid_current_all&bid=42&o_type=current&pool=three&is_match=1'\
    '&c_type=0&h={home}&d={drew}&a={away}&_=%s'
