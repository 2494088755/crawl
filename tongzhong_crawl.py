import pymysql
import requests
from requests import ReadTimeout
import pandas as pd

from music_crawl import download_music

search_url = 'https://music-api.tonzhon.com/songs_of_artist/'
get_download_url_api = 'https://music-api.tonzhon.com/song_file/'

search_m = 'https://music-api.tonzhon.com/search/m/'
search_n = 'https://music-api.tonzhon.com/search/n/'
search_q = 'https://music-api.tonzhon.com/search/q/'
search_k = 'https://music-api.tonzhon.com/search/k/'


# key = '杨丞琳'
# try:
#     songs = requests.get(search_url + key, timeout=0.5).json()['songs']
# except ReadTimeout as e:
#     songs1 = requests.get(search_m + key).json()['data']['songs']
#     songs2 = requests.get(search_n + key).json()['data']['songs']
#     songs3 = requests.get(search_q + key).json()['data']['songs']
#     songs4 = requests.get(search_k + key).json()['data']['songs']
#     songs = songs1 + songs2 + songs3 + songs4
#
# song_list = []
# for song in songs:
#     singers = ''
#     for singer in song['artists']:
#         singers += singer['name'] + '/'
#     song_list.append([song['newId'], song['name'], singers[:-1]])
#
# header = ['id', 'name', 'singer']
# # 设置value的显示长度为100，默认为50
# pd.set_option('max_colwidth', 100)
# df = pd.DataFrame(columns=header, data=song_list)
# print(df.to_markdown())
# index = input('输入序号下载指定歌曲:')
# id_ = df.loc[int(index)]['id']
# song_name = df.loc[int(index)]['name']
# singer_name = df.loc[int(index)]['singer']
# print('正在下载：' + song_name + ' - ' + singer_name)
# download_url = requests.get(get_download_url_api + id_).json()['data']
# print('https:' + download_url)
# download_music('https:' + download_url, song_name, singer_name)
# print('下载完成')


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
        song_list.append([song['newId'], song['name'], singers[:-1]])
    return song_list


def print_list(song_list):
    header = ['id', 'name', 'singer']
    # 设置value的显示长度为100，默认为50
    pd.set_option('max_colwidth', 100)
    df = pd.DataFrame(columns=header, data=song_list)
    print(df.to_markdown())
    return df


def download(df):
    index = input('输入序号下载指定歌曲:')
    id_ = df.loc[int(index)]['id']
    song_name = df.loc[int(index)]['name']
    singer_name = df.loc[int(index)]['singer']
    print('正在下载：' + song_name + ' - ' + singer_name)
    download_url = requests.get(get_download_url_api + id_).json()['data']
    print('https:' + download_url)
    download_music('https:' + download_url, song_name, singer_name)
    print('下载完成')


def run(key):
    download(print_list(get_song_list(key)))
