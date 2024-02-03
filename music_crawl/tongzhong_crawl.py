import os

import pandas as pd
import pymysql
import requests
from requests import ReadTimeout

from music_crawl.zz_music_crawl import download_music

search_url = 'https://music-api.tonzhon.com/songs_of_artist/'
get_download_url_api = 'https://music-api.tonzhon.com/song_file/'
get_song_lyrics_api = 'https://music-api.tonzhon.com/lyrics/'
search_m = 'https://music-api.tonzhon.com/search/m/'
search_n = 'https://music-api.tonzhon.com/search/n/'
search_q = 'https://music-api.tonzhon.com/search/q/'
search_k = 'https://music-api.tonzhon.com/search/k/'


def get_song_list(key):
    try:
        songs = requests.get(search_url + key, timeout=0.5).json()['songs']
    except ReadTimeout as e:
        songs1 = requests.get(search_m + key).json()['data']['songs']
        songs2 = requests.get(search_n + key).json()['data']['songs']
        songs3 = requests.get(search_q + key).json()['data']['songs']
        songs4 = requests.get(search_k + key).json()['data']['songs']
        songs = songs1 + songs2 + songs3 + songs4
    song_list = []
    for song in songs:
        singers = ''
        for singer in song['artists']:
            singers += singer['name'] + '/'
        # download_url = requests.get(get_download_url_api + song['newId']).json()['data']
        song_list.append([song['name'], song['newId'], singers[:-1]])
    connect = pymysql.connect(host='localhost', user='root', password='root', db='music')
    cursor = connect.cursor()
    sql = "insert into tb_music(song_name,download_url,singer_name) values(%s,%s,%s)"
    cursor.executemany(sql, song_list)
    connect.commit()
    cursor.close()
    connect.close()
    return song_list


def print_list(song_list):
    header = ['name', 'id', 'singer']
    # 设置value的显示长度为100，默认为50
    pd.set_option('max_colwidth', 100)
    df = pd.DataFrame(columns=header, data=song_list)
    print(df.to_markdown())
    return df


def download(df):
    # 输入序号下载指定歌曲
    index = input('输入序号下载指定歌曲:')
    # 从数据框中获取指定序号的歌曲id、歌曲名和歌手名
    id_ = df.loc[int(index)]['id']
    song_name = df.loc[int(index)]['name']
    singer_name = df.loc[int(index)]['singer']
    # 打印歌曲id、歌曲名和歌手名
    print(id_)
    print(song_name)
    print(singer_name)
    # 打印正在下载的歌曲信息
    print('正在下载：' + song_name + ' - ' + singer_name)
    # 获取歌曲下载链接
    download_url = requests.get(get_download_url_api + id_).json()['data']
    # 如果下载链接不是以'https:'开头，则在前面添加'https:'
    if 'https:' not in download_url:
        download_url = 'https:' + download_url
    # 下载歌曲
    download_music(download_url, song_name, singer_name)
    # 打印下载完成
    print('下载完成')


def run(key):
    print('正在搜索：' + key)
    download(print_list(get_song_list(key)))


if __name__ == '__main__':
    run('王菲')
