import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


class GeQubeo:
    base_url = 'https://www.gequbao.com/'
    search_url = base_url + '/s/'

    def get_songs(self, keyword: str):
        soup = BeautifulSoup(requests.get(self.search_url + keyword).text, 'html.parser')
        find_all = soup.find_all(attrs={'class': 'col-5 col-content'})
        songs = []
        sid = 0
        for item in find_all:
            songname = item.find_next('a').text.strip()
            singer = item.find_next(attrs={'class': 'text-success col-4 col-content'}).text.strip()
            href_ = item.find_next('a').attrs['href']
            music_url = self.base_url + href_
            songs.append({'id': sid, 'songname': songname, 'singer': singer, 'music_url': music_url})
            sid += 1
        self.check(songs)

    def check(self, songs: list):
        if songs.__len__() > 0:
            print('共找到{}首歌曲'.format(songs.__len__()))
            for i in songs:
                print(i)
            self.download(songs)
        else:
            print('没有找到歌曲')

    def download(self, songs: list):
        input_id = eval(input('输入id下载歌曲/输入n重新搜索'))
        if input_id == 'n':
            return
        for i in songs:
            if i['id'] == input_id:
                print(i['music_url'])
                print('开始下载')
                driver = webdriver.Edge()
                driver.get(i['music_url'])
                href = driver.find_element(by=By.ID, value='btn-download-mp3').get_attribute('href')
                song_info = driver.find_element(by=By.ID, value='btn-download-mp3').get_attribute('download')
                print(song_info)
                print(href)
                driver.close()
                if href is None:
                    print('下载失败')
                    break
                with open(song_info, 'wb') as f:
                    f.write(requests.get(href).content)
                    f.close()
                    print('下载完成')
                    break


if __name__ == '__main__':
    while True:
        GeQubeo().get_songs(input('输入关键字搜索歌曲').strip())
        if input('是否继续搜索') == 'n':
            break
