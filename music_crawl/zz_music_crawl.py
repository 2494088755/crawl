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
    # 创建一个包含音乐标题的列表
    music = [music_title]
    # 根据音乐链接生成音乐播放地址
    music_href = 'https://zz123.com/xplay/?act=songplay&id={}&email'.format(music_href.split('/')[-1].split('.')[0])
    # 将歌手名字添加到音乐列表中
    music.append(music_href)
    music.append(singer_name)
    # 返回音乐列表
    return music


def find_music_on_db_by_search_key(search_key):
    # 连接数据库
    cursor = connect.cursor()
    # 构建SQL语句
    sql = '''select * from tb_music where singer_name like %s"%%" or song_name like %s"%%"'''
    # 设置查询参数
    val = (search_key, search_key)
    # 执行查询语句
    cursor.execute(sql, val)
    # 获取所有查询结果
    results = cursor.fetchall()
    # 关闭游标
    cursor.close()
    # 返回查询结果
    return results


def download_music(url, song_name, singer_name):
    # 如果歌手名中包含斜杠，则将其替换为空格
    if '/' in singer_name:
        singer_name = singer_name.replace('/', ' ')
    # 如果歌手名对应的文件夹不存在，则创建该文件夹
    if not os.path.exists(f'D:\\音乐\\{singer_name}'):
        os.mkdir(f'D:\\音乐\\{singer_name}')
    # 如果url以'http'开头，则直接使用该url下载音乐内容
    if 'http' in url:
        content = requests.get(url).content
    # 如果url不以'http'开头，则先通过API获取下载地址，再使用该地址下载音乐内容
    else:
        download_url = requests.get(tongzhong_crawl.get_download_url_api + url).json()['data']
        content = requests.get(download_url).content
    # 将音乐内容写入文件
    with open('D:\\音乐\\{}\\{}-{}.mp3'.format(singer_name, song_name, singer_name), 'wb') as f:
        f.write(content)


def download_music_by_id(results, search_key):
    # 如果搜索结果不为空
    if results.__len__() > 0:
        # 打印每个搜索结果
        for result in results:
            print(result)
        # 如果用户选择换源搜索
        if input('没找到？是否换源搜索y/n') == 'y':
            # 运行换源搜索函数
            tongzhong_crawl.run(search_key)
            sys.exit(0)
        # 输入序号
        id_ = int(input("输入序号下载歌曲："))
        # 遍历搜索结果
        for result in results:
            # 如果输入的序号与当前结果的序号相等
            if id_ == result[0]:
                print('下载中...')
                print(result)
                # 调用下载音乐的函数
                download_music(result[2], result[1], result[3])
                print('下载完成')
                # 关闭连接
                connect.close()
                sys.exit(0)
        # 如果没有找到序号为id_的歌曲
        print('没有id为{}的歌曲'.format(id_))
    else:
        # 如果在数据库中没有找到歌曲
        print('未在数据库中找到歌曲')
        # 打印正在爬取歌曲的信息
        print('正在爬取歌曲...')


def choice():
    """
    选择歌曲并下载
    :return:
    """
    cursor = connect.cursor()  # 创建游标对象
    search_key = input("请输入关键词：")  # 获取用户输入的关键词
    results = find_music_on_db_by_search_key(search_key)  # 在数据库中根据关键词搜索歌曲
    download_music_by_id(results, search_key)  # 根据搜索结果下载歌曲
    # music_list = search(search_key)  # 使用其他搜索源搜索歌曲
    music_list = []  # 创建空的音乐列表
    if music_list is None or music_list.__len__() == 0:  # 如果音乐列表为空
        print('没有歌曲')  # 打印提示信息
        print('切换搜索源...')
        tongzhong_crawl.run(search_key)  # 使用其他搜索源搜索歌曲
        sys.exit(0)  # 退出程序
    sql = "insert into tb_music(song_name,download_url,singer_name) values(%s,%s,%s)"  # SQL语句，用于将歌曲信息插入数据库
    cursor.executemany(sql, music_list)  # 执行SQL语句，将歌曲信息插入数据库
    connect.commit()  # 提交数据库事务
    results = find_music_on_db_by_search_key(search_key)  # 在数据库中根据关键词搜索歌曲
    download_music_by_id(results, search_key)  # 根据搜索结果下载歌曲
    cursor.close()  # 关闭游标对象
    connect.close()  # 关闭数据库连接


# search_key = input("请输入关键词：")
if __name__ == '__main__':
    choice()
