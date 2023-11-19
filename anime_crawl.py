import os.path
import re
import time

import pandas as pd
import pymysql
import redis
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm

import proxy_util

search_url = 'https://www.dmdm0.com/search/-------------.html?wd='
base_url = 'https://www.dmdm0.com'
video_list = []
connect = pymysql.connect(host='localhost', user='root', password='root', db='video')
redis = redis.Redis(host='localhost', port=6379, db=0)


def get_search_list(key):
    """
    获取搜索列表
    :param key:
    :return:
    """
    search_list = []
    get = proxy_util.get(search_url + key)
    soup = BeautifulSoup(get, 'html.parser')
    ul = soup.find('ul', attrs={'class': 'stui-vodlist__media col-pd clearfix'})
    index = 0
    for li in ul.find_all('li'):
        search_one = []
        title = li.find('h3', attrs={'class': 'title'}).text
        href = base_url + li.find('h3', attrs={'class': 'title'}).a['href']
        search_one.append(index)
        search_one.append(title)
        search_one.append(href)
        search_list.append(search_one)
        index += 1
    for i in search_list:
        print(i)
    if search_list.__len__() == 0:
        print('没有找到相关视频')
        return
    input_index = input('请输入你要下载的视频序号：')
    if input_index.isdigit():
        if int(input_index) < search_list.__len__():
            return get_all_video_url(search_list[int(input_index)][2])
        else:
            print('输入序号超出范围')
            return


def get_all_video_url(url):
    """
    获取所有视频的url
    :return:
    """
    video_url_list = []
    req = proxy_util.get(url)
    soup = BeautifulSoup(req, 'html.parser')
    ul = soup.find('ul', attrs={'class': 'stui-content__playlist clearfix'})
    li_list = ul.find_all('li')
    designate_list = []
    index = 0
    for i in li_list:
        video_info = [index, i.text, base_url + i.a['href']]
        index += 1
        video_url_list.append(base_url + i.a['href'])
        designate_list.append(video_info)
    for i in designate_list:
        print(i)
    input_method = input('请输入你要下载的方式：1.指定下载 2.全部下载')
    if input_method == '1':
        input_index = input('请输入你要下载的视频序号：')
        if input_index.isdigit():
            if int(input_index) < designate_list.__len__():
                return [designate_list[int(input_index)][2]]
            else:
                print('输入序号超出范围')
                return
    elif input_method == '2':
        return video_url_list
    else:
        print('输入错误')


def get_one_video_url(url):
    """
    获取视频的m3u8解析url
    :param url:
    :return:
    """
    get = proxy_util.get(url)
    soup = BeautifulSoup(get, 'html.parser')
    find = soup.find_all('script')
    title = soup.find('h1', attrs={'class': 'title'}).text
    active = soup.find('ul', attrs={'class': 'stui-content__playlist clearfix'}).find('li',
                                                                                      attrs={'class': 'active'}).text
    pattern = r'"url":"(.*?)"'
    video_info = []
    redis.set('title', title)
    for i in find:
        match = re.search(pattern, i.text)
        if match:
            print("找到了匹配：", match.group())
            video_url = 'https://danmu.yhdmjx.com/m3u8.php?url=' + match.group().split('"url":"')[1].split('"')[0]
            if video_url.__len__() > 100:
                src = get_download_url(video_url)
                video_info.append(title)
                video_info.append(active)
                video_info.append(src)
                video_list.append(video_info)
                redis.set(f'{title}', str(video_list))
                print(video_info)


def get_download_url(video_url):
    """
    获取下载链接
    :param video_url:
    :return:
    """
    driver = webdriver.Edge()
    driver.get(video_url)
    while True:
        try:
            video = driver.find_element(by='tag name', value='video')
            break
        except Exception as e:
            print('未渲染，正在重试')
            time.sleep(1)
    src = video.get_attribute('src')
    driver.close()
    return src


def save_on_mysql():
    """
    保存到mysql
    :return:
    """
    cursor = connect.cursor()
    sql = "insert into tb_video(title,number,url) values(%s,%s,%s)"
    cursor.executemany(sql, video_list)
    connect.commit()
    cursor.close()
    connect.close()


def save_on_excel(nested_list):
    """
    保存到excel
    :param nested_list:
    :return:
    """
    pd.DataFrame(nested_list, columns=['title', 'number', 'url']).to_excel(f'{redis.get("title").decode("utf-8")}.xlsx',
                                                                           index=False)


def download_video(nested_list):
    """
    下载视频
    :param nested_list:
    :return:
    """
    for video_info in nested_list:
        print(video_info)
        resp = requests.get(video_info[2], stream=True)
        total = int(resp.headers.get('content-length', 0))
        if not os.path.exists(f'D:\\视频\\{video_info[0]}'):
            os.mkdir(f'D:\\视频\\{video_info[0]}')
        with open(f'D:\\视频\\{video_info[0]}\\' + video_info[0] + video_info[1] + '.mp4', 'wb') as file, tqdm(
                desc=video_info[0] + video_info[1] + '.mp4',
                total=total,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for data in resp.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)


if __name__ == '__main__':
    try:
        search_key = input('请输入你要搜索的视频：')
        for one_url in get_search_list(search_key):
            get_one_video_url(one_url)
        nested_list = eval(redis.get(f'{redis.get("title").decode("utf-8")}').decode('utf-8'))
        # 下载视频
        download_video(nested_list)
        redis.delete(f'{redis.get("title").decode("utf-8")}')
        redis.delete('title')
    except Exception as e:
        print(e)
    finally:
        connect.close()
        redis.close()
