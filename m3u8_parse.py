import os.path
import queue
import re
import threading
import time

import requests


def get_list(url):
    get = requests.get(url)
    ts_list = re.findall(r'(https?://\S+)', get.text)
    if len(ts_list) == 0:
        rsplit_ = url.rsplit('/', 1)[0]
        ts_list = re.findall(r'(.*\.ts)', get.text)
        ts_list = [rsplit_ + '/' + ts for ts in ts_list]
    return ts_list


def download(thread_name, q):
    os.path.exists('D:\\ts') or os.mkdir('D:\\ts')
    ts = q.get()
    print(thread_name + '-开始下载' + ts)
    with open('D:\\ts\\' + ts.split('/')[-1], 'wb') as f:
        f.write(requests.get(ts).content)
    print(thread_name + '-下载完成')
    print('剩余' + str(q.qsize()) + '个ts文件')


def merge():
    file_name = input('输入保存文件名:')
    cmd = f'copy /b D:\\ts\\*.ts D:\\ts\\{file_name}.mp4'
    os.system(cmd)
    # 将ts文件删除
    for ts in os.listdir('D:\\ts'):
        if ts.endswith('.ts'):
            os.remove('D:\\ts\\' + ts)
    print('合并完成')


class MyThread(threading.Thread):
    def __init__(self, thread_name, q):
        super(MyThread, self).__init__()
        self.thread_name = thread_name
        self.q = q

    def run(self):
        while True:
            if self.q.empty():
                break
            download(self.thread_name, self.q)


if __name__ == '__main__':
    tss = get_list(input('输入m3u8地址:'))
    start = time.time()
    threads = []
    q = queue.Queue(len(tss))
    for t in tss:
        q.put(t)
    for i in range(5):
        thread = MyThread(f'thread-{i}', q)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    end = time.time()
    print("共耗时：{} s".format(end - start))
    merge()
