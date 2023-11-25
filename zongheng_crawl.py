import requests
from bs4 import BeautifulSoup

import proxy_util

base_url = 'https://www.zongheng.com/'
top200_url = base_url + '/rank?nav=recommend&rankType=6'

session = requests.session()
session.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 '
                  'Safari/537.36 Edg/119.0.0.0',
    'Cookie': 'ZHID=65597F40C7316EC1D806BDE3C2E6E737; zh_visitTime=1700131436386; '
              'Hm_lvt_c202865d524849216eea846069349eb9=1700131437; zhffr=www.bing.com; '
              'sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218bd7baf75066c-0cb007945201bf-4c657b58-1327104'
              '-18bd7baf7511048%22%2C%22%24device_id%22%3A%2218bd7baf75066c-0cb007945201bf-4c657b58-1327104'
              '-18bd7baf7511048%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6'
              '%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.bing.com%2F%22'
              '%2C%22%24latest_referrer_host%22%3A%22www.bing.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA'
              '%E5%8F%96%E5%88%B0%E5%80%BC%22%7D%7D; '
              'acw_tc=1a0c398517007445349332670ea7213420d8e0051dee2527e6582bb9500c89 '

}
data = {
    'cateFineId': 0,
    'cateType': 0,
    'pageNum': 1,
    'pageSize': 200,
    'period': 0,
    'rankNo': '',
    'rankType': 6,
}
result_list = session.post('https://www.zongheng.com/api/rank/details', data=data).json()['result']['resultList']

for result in result_list:
    print('排名：' + str(result['orderNo']), end=' ')
    print('书名：' + str(result['bookName']), end=' ')
    print('作者：' + str(result['pseudonym']))

