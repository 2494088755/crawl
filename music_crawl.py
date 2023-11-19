import os.path
import sys

import time

import pymysql
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

import proxy_util

base_url = 'https://zz123.com'
search_url = base_url + '/search/?key='
connect = pymysql.connect(host='localhost', user='root', password='root', db='music')


def search(key):
    url = search_url + key
    req = proxy_util.get(url)
    soup = BeautifulSoup(req, 'html.parser')
    all_singer_music = soup.find_all('div', attrs={'class': 'item-desc'})
    singer_name_list = soup.find_all('div', attrs={'class': 'singername text-ellipsis color-link-content-secondary'})
    singer_href = ''
    for name in singer_name_list:
        singer_name = name.text.replace('\n', '')
        if singer_name == key:
            singer_href = base_url + name.a['href']
            break
    if singer_href == '':
        print('没有找到歌手')
        return
    if all_singer_music.__len__() == 20:
        return selenium_crawl(singer_href)
    music_list = []
    for i in all_singer_music:
        beautiful_soup = BeautifulSoup(str(i), 'html.parser')
        music_title = \
            beautiful_soup.find('div', attrs={'class': 'songname text-ellipsis color-link-content-primary'}).find('a')[
                'title']
        music_href = \
            beautiful_soup.find('div', attrs={'class': 'songname text-ellipsis color-link-content-primary'}).find('a')[
                'href']
        singer_name = beautiful_soup.find('div',
                                          attrs={'class': 'singername text-ellipsis color-link-content-secondary'}).text
        singer_href = beautiful_soup.find('div',
                                          attrs={'class': 'singername text-ellipsis color-link-content-secondary'}).a[
            'href']
        singer_name = singer_name.replace('\n', '')
        music_list.append(save_on_list(music_title, music_href, singer_name, singer_href))
    return music_list


def selenium_crawl(url):
    driver = webdriver.Edge()
    driver.get(url)
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
        singer_href = a_list[0].get_property('href')
        singer_name = singer_name.replace('\n', '')
        music_list.append(save_on_list(music_title, music_href, singer_name, singer_href))
    driver.quit()
    return music_list


def save_on_list(music_title, music_href, singer_name, singer_href):
    music = [music_title]
    music_href = 'https://zz123.com/xplay/?act=songplay&id={}&email'.format(music_href.split('/')[-1].split('.')[0])
    music.append(music_href)
    music.append(singer_name)
    # music.append(base_url + singer_href)
    return music


def search_one_music(music_list, key):
    for music in music_list:
        if key in music[0]:
            return music
    return None


def find_music_on_db_by_singer_name(singer_name):
    cursor = connect.cursor()
    sql = '''select * from tb_music where singer_name like %s"%%"'''
    cursor.execute(sql, singer_name)
    results = cursor.fetchall()
    return results


def download_music(url, song_name, singer_name):
    if not os.path.exists(f'D:\\音乐\\{singer_name}'):
        os.mkdir(f'D:\\音乐\\{singer_name}')
    content = proxy_util.get_content(url)
    with open('D:\\音乐\\{}\\{}-{}.mp3'.format(singer_name, song_name, singer_name), 'wb') as f:
        f.write(content)


def download_music_by_id(results):
    if results.__len__() > 0:
        for result in results:
            print(result)
        song_name = input("请输入歌曲名字：")
        is_exist = False
        for result in results:
            if song_name in result[1]:
                is_exist = True
                print(result)
        if not is_exist:
            print('没有{}该歌曲'.format(song_name))
            sys.exit(0)
        id_ = int(input("输入序号下载歌曲："))
        for result in results:
            if id_ == result[0]:
                print('下载中...')
                download_music(result[2], result[1], result[3])
                print('下载完成')
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
    singer_name = input("请输入歌手名字：")
    results = find_music_on_db_by_singer_name(singer_name)
    download_music_by_id(results)
    music_list = search(singer_name)
    sql = "insert into tb_music(song_name,download_url,singer_name) values(%s,%s,%s)"
    cursor.executemany(sql, music_list)
    connect.commit()
    results = find_music_on_db_by_singer_name(singer_name)
    download_music_by_id(results)
    cursor.close()
    connect.close()


if __name__ == '__main__':
    choice()
