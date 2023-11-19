import os.path
import threading
import uuid

from bs4 import BeautifulSoup

import proxy_util

base_url = 'https://wallpaperscraft.com/'


def site_page(page):
    print('开始下载第' + str(page) + '页')
    url = base_url + 'all/page' + str(page)
    # req = requests.get(url, headers=header)
    req = proxy_util.get(url)
    soup = BeautifulSoup(req, 'html.parser')
    find_all = soup.find_all('a', attrs={'class': 'wallpapers__link'})
    print('第' + str(page) + '页共有' + str(len(find_all)) + '张图片')
    for i in find_all:
        img_detail(i['href'], page)


def img_detail(url, page):
    url = base_url + url
    # req = requests.get(url, headers=header)
    req = proxy_util.get(url)
    soup = BeautifulSoup(req, 'html.parser')
    find_all = soup.find_all('a', attrs={'class': 'resolutions__link'})
    get_hd_img(find_all[-1]['href'], page)
    return find_all[-1]['href']


def get_hd_img(url, page):
    # req = requests.get(base_url + url, headers=header)
    req = proxy_util.get(base_url + url)
    soup = BeautifulSoup(req, 'html.parser')
    find = soup.find('a', attrs={'class': 'gui-button gui-button_full-height'})
    try:
        download(find['href'], page)
    except Exception:
        print('下载失败，重新下载')
        # time.sleep(3)
        get_hd_img(url, page)


def download(url, page):
    print('下载中：' + url + '\n页数为：' + str(page))
    if not os.path.exists(f'D:\\图片\\wallpaperscraft\\{page}\\'):
        os.makedirs(f'D:\\图片\\wallpaperscraft\\{page}\\')
    with open(f'D:\\图片\\wallpaperscraft\\{page}\\' + uuid.uuid4().hex + '.jpg', 'wb') as f:
        f.write(proxy_util.get_content(url))
    print('下载完成,\n页数为：' + str(page))


class MyThread(threading.Thread):
    def __init__(self,page):
        threading.Thread.__init__(self)
        self.page = page

    def run(self):
        for i in self.page:
            site_page(i)


if __name__ == '__main__':
    index_list = [(1, 2, 3, 4, 5), (6, 7, 8, 9, 10), (11, 12, 13, 14, 15), (16, 17, 18, 19, 20)]
    threads = []
    for i in range(1, 5):
        thread = MyThread(index_list[i - 1])
        # 开启新线程
        thread.start()
        # 添加新线程到线程列表
        threads.append(thread)

    # 等待所有线程完成
    for thread in threads:
        thread.join()
