import os.path
import sys

import time

import pymysql
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

import proxy_util
import tongzhong_crawl

base_url = 'https://zz123.com'
search_url = base_url + '/search/?key='
connect = pymysql.connect(host='localhost', user='root', password='root', db='music')


def search(key):
    url = search_url + key
    req = requests.get(url, headers=proxy_util.headers).text
    soup = BeautifulSoup(req, 'html.parser')
    all_singer_music = soup.find_all('div', attrs={'class': 'item-desc'})
    if all_singer_music.__len__() == 20:
        return selenium_crawl(url)
    if all_singer_music.__len__() == 0:
        print('zz源没有找到')
        return None
    music_list = []
    for music in all_singer_music:
        song_name = music.find('div', attrs={'class': 'songname text-ellipsis color-link-content-primary'}).a['title']
        singer_name = music.find('div', attrs={'class': 'singername text-ellipsis color-link-content-secondary'}).a[
            'title']
        song_href = music.find('div', attrs={'class': 'songname text-ellipsis color-link-content-primary'}).a['href']
        music_list.append(save_on_list(song_name, song_href, singer_name))
    return music_list


def selenium_crawl(url):
    driver = webdriver.Edge()
    driver.get(url)
    if driver.title == '404':
        print('zz源没有找到')
        driver.close()
        return None
    # 定义一个初始值
    temp_height = 0
    music_list = []
    while True:
        # 循环将滚动条下拉
        driver.execute_script("window.scrollBy(0,800)")
        # sleep一下让滚动条反应一下
        time.sleep(0.5)
        # 获取当前滚动条距离顶部的距离
        check_height = driver.execute_script(
            "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")
        # 如果两者相等说明到底了
        if check_height == temp_height:
            break
        temp_height = check_height
    item_desc_list = driver.find_elements(by=By.CLASS_NAME, value='item-desc')
    for item in item_desc_list:
        a_list = item.find_elements(by=By.TAG_NAME, value='a')
        if a_list.__len__() == 0:
            continue
        music_title = a_list[0].get_property('title')
        music_href = a_list[0].get_property('href')
        singer_name = a_list[1].get_property('title')
        singer_name = singer_name.replace('\n', '')
        music_list.append(save_on_list(music_title, music_href, singer_name))
    driver.close()
    return music_list


def save_on_list(music_title, music_href, singer_name):
    music = [music_title]
    music_href = 'https://zz123.com/xplay/?act=songplay&id={}&email'.format(music_href.split('/')[-1].split('.')[0])
    music.append(music_href)
    music.append(singer_name)
    return music


def find_music_on_db_by_search_key(search_key):
    cursor = connect.cursor()
    sql = '''select * from tb_music where singer_name like %s"%%" or song_name like %s"%%"'''
    val = (search_key, search_key)
    cursor.execute(sql, val)
    results = cursor.fetchall()
    cursor.close()
    return results


def download_music(url, song_name, singer_name):
    if '/' in singer_name:
        singer_name = singer_name.replace('/', ' ')
    if not os.path.exists(f'D:\\音乐\\{singer_name}'):
        os.mkdir(f'D:\\音乐\\{singer_name}')
    if 'http' in url:
        content = requests.get(url).content
    else:
        download_url = requests.get(tongzhong_crawl.get_download_url_api + url).json()['data']
        content = requests.get(download_url).content
    with open('D:\\音乐\\{}\\{}-{}.mp3'.format(singer_name, song_name, singer_name), 'wb') as f:
        f.write(content)


def download_music_by_id(results, search_key):
    if results.__len__() > 0:
        for result in results:
            print(result)
        if input('没找到？是否换源搜索y/n') == 'y':
            tongzhong_crawl.run(search_key)
            sys.exit(0)
        id_ = int(input("输入序号下载歌曲："))
        for result in results:
            if id_ == result[0]:
                print('下载中...')
                download_music(result[2], result[1], result[3])
                print('下载完成')
                connect.close()
                sys.exit(0)
        print('没有id为{}的歌曲'.format(id_))
    else:
        print('未在数据库中找到歌曲')
        print('正在爬取歌曲...')


def choice():
    """
    选择歌曲并下载
    :return:
    """
    cursor = connect.cursor()
    search_key = input("请输入关键词：")
    results = find_music_on_db_by_search_key(search_key)
    download_music_by_id(results, search_key)
    music_list = search(search_key)
    if music_list is None or music_list.__len__() == 0:
        print('没有歌曲')
        print('切换搜索源...')
        tongzhong_crawl.run(search_key)
        sys.exit(0)
    sql = "insert into tb_music(song_name,download_url,singer_name) values(%s,%s,%s)"
    cursor.executemany(sql, music_list)
    connect.commit()
    results = find_music_on_db_by_search_key(search_key)
    download_music_by_id(results, search_key)
    cursor.close()
    connect.close()


# search_key = input("请输入关键词：")
if __name__ == '__main__':
    choice()
