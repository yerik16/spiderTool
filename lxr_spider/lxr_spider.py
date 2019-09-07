# -*- coding:utf-8 -*-

from urllib.error import URLError  # 异常处理模块，捕获错误
from urllib.request import ProxyHandler, build_opener  # 代理IP模块
import json
import pandas as pd
import time
import datetime
import random
import urllib.request
from bs4 import BeautifulSoup
import requests



def random_user_agent():
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; ARM; Trident/6.0)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30;'
        ' .NET CLR 3.0.04506.648)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; InfoPath.1',
        'Mozilla/4.0 (compatible; GoogleToolbar 5.0.2124.2070; Windows 6.0; MSIE 8.0.6001.18241)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; EasyBits Go v1.0; InfoPath.1;'
        ' .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; '
        '.NET CLR 3.0.04506)'
    ]
    return random.choice(agents)

def random_proxies():
	ports = ['1080', '1081', '1082', '1083']
	random_port = random.choice(ports)
	proxies = {
		'http':'127.0.0.1:%s' % random_port
	}
	return proxies





def threeTypeCB(opener):
    #global str, df, ndarray, list, each, dict, dict2, i, newDf
    global newDf
    # TODO：可转债筛选
    response = opener.open(
        'https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t=1567040758309')  # 此处的open方法同urllib的urlopen方法
    str = response.read().decode('utf-8')
    json1 = json.loads(str)
    df = pd.DataFrame(json1)
    df = df.drop(['page', 'total'], axis=1)
    ndarray = df['rows'].values
    # 将ndarray的每个cell放入list
    list = []
    for each in ndarray:
        dict = each['cell']
        list.append(dict)
    # 把list放入dict
    dict2 = {}
    for i in range(len(list)):
        dict2[i] = [list[i]['bond_id'], list[i]['bond_nm'], list[i]['price'], list[i]['premium_rt'],
                    list[i]['rating_cd'], list[i]['convert_cd'], list[i]['year_left'], list[i]['ytm_rt_tax'],
                    list[i]['price_tips']]
    # 再将dict放入dataframe
    newDf = pd.DataFrame.from_dict(dict2, orient='index',
                                   columns=['bond_id', 'bond_nm', 'price', 'premium_rt', 'rating_cd', 'convert_cd',
                                            'year_left', 'ytm_rt_tax', 'price_tips'])
    i = 0
    for each in newDf.values:
        if (each[1].__contains__('EB') or each[8] == '待上市' or (
                each[4] == 'AA' or each[4] == 'AAA' or each[4] == 'AA+') == False):  # 去掉可交换债
            newDf = newDf.drop([i])
        # if(each[8] == '待上市'):
        #     newDf = newDf.drop([i])
        # if((each[4] == 'AA' or each[4] == 'AAA' or each[4] == 'AA+') == False): #根据评级筛选
        #     newDf = newDf.drop([i])
        i = i + 1

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # 数据类型转换
    newDf['ytm_rt_tax'] = newDf['ytm_rt_tax'].map(lambda x: float(x[0:-1]) / 100)
    newDf['premium_rt'] = newDf['premium_rt'].map(lambda x: float(x[0:-1]) / 100)
    newDf['price'] = newDf['price'].map(lambda x: float(x))
    # 防御型
    defence = newDf.sort_values(by='ytm_rt_tax', axis=0, ascending=False).head(3)
    print('防御型:')
    print(defence[['bond_id', 'bond_nm', 'price', 'premium_rt', 'rating_cd', 'year_left', 'ytm_rt_tax']])
    # 平衡型
    balance = newDf[newDf['ytm_rt_tax'] > 0]
    balance = balance[balance['ytm_rt_tax'] < 0.03]
    balance = balance[balance['premium_rt'] < 0.05].head(5)
    print('平衡型:')
    print(balance[['bond_id', 'bond_nm', 'price', 'premium_rt', 'rating_cd', 'year_left', 'ytm_rt_tax']])
    # 进攻型
    indexs = newDf.loc[(newDf['convert_cd'] == '未到转股期')].index  # 过滤未到转股期
    attack = newDf.drop(indexs)
    attack = attack[attack['premium_rt'] < 0.02].sort_values(by='premium_rt', axis=0, ascending=True).head(2)
    print('进攻型:')
    print(attack[['bond_id', 'bond_nm', 'price', 'premium_rt', 'rating_cd', 'year_left', 'ytm_rt_tax']])

    # TODO:四要素类型   AA级以上的    溢价率＜10%     到期收益率＞0     价格110以下
    fourElement = newDf[newDf['ytm_rt_tax'] > 0]    #到期收益率＞0
    fourElement = fourElement[fourElement['premium_rt'] < 0.1]  #溢价率＜10%
    fourElement = fourElement[fourElement['price'] < 110]
    print('四要素类型：')
    print(fourElement[['bond_id', 'bond_nm', 'price', 'premium_rt', 'rating_cd', 'year_left', 'ytm_rt_tax']])

    def random_user_agent():
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; ARM; Trident/6.0)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30;'
            ' .NET CLR 3.0.04506.648)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; InfoPath.1',
            'Mozilla/4.0 (compatible; GoogleToolbar 5.0.2124.2070; Windows 6.0; MSIE 8.0.6001.18241)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; EasyBits Go v1.0; InfoPath.1;'
            ' .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; '
            '.NET CLR 3.0.04506)'
        ]
        return random.choice(agents)


def random_proxies():
    ports = ['1080', '1081', '1082', '1083']
    random_port = random.choice(ports)
    proxies = {
        # 'https': 'https://127.0.0.1:%s' % random_port,
        'http': 'http://127.0.0.1:%s' % random_port,
    }
    return proxies




# 请求网站
try:
    # s = requests.Session()
    # headers = {'User-Agent': random_user_agent()}
    # proxies = random_proxies()
    #
    # profile_url = ''
    # resp = s.get(profile_url, headers=headers, proxies=proxies, timeout=6)


    #TODO:各宽基指数长投温度
    #把所有stockCode放于集合
    file = open('latest.txt')
    line = file.readline()
    json_ = json.loads(line)
    df = pd.DataFrame(json_)
    print(df.values)
    for each in df.values:
        print(each['stockCode'])






except URLError as e:
    print(e.reason)