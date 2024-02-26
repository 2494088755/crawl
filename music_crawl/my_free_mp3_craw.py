import bs4
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By


class MyFreeMP3:
    search_url = 'http://tools.liumingye.cn/music/#/search/M/song/'

    def __init__(self, keyword):
        self.search_url = self.search_url + keyword

    def download(self):
        driver = webdriver.Edge()
        driver.get(self.search_url)
        songs = []
        index = 1
        while True:
            try:
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                root_div = driver.find_element(by=By.XPATH,
                                               value='//*[@id="content"]/div/div/div[3]/div[2]').get_attribute(
                    'innerHTML')
                soup = bs4.BeautifulSoup(root_div, 'html.parser')
                find_all = soup.find_all(
                    attrs={'class': 'arco-row arco-row-align-center arco-row-justify-start h-12 px-2'})
                for i in find_all:
                    title = i.find_next(attrs={'class', 'text-sm'}).text
                    # singer = i.find_next(attrs={'class', 'hover:underline cursor-pointer'}).text
                    singer = i.find_next('mark').text
                    songs.append({'index': index, 'title': title, 'singer': singer})
                    index += 1
                break
            except Exception as e:
                print(e)

        for i in songs:
            print(i)
        index = eval(input('输入序号下载:'))

        while True:
            try:
                element = driver.find_element(by=By.XPATH,
                                              value=f'//*[@id="content"]/div/div/div[3]/div[2]/div[{index}]/div/div[6]/button')
                element.click()
                break
            except Exception as e:
                print(e)
        while True:
            try:
                driver.find_elements(by=By.CLASS_NAME, value='icon')[-1].click()
                break
            except Exception as e:
                print(e)

        while True:
            try:
                download_url = driver.find_elements(by=By.CLASS_NAME, value='arco-space-item')[0].find_element(
                    by=By.TAG_NAME,
                    value='a').get_attribute(
                    'href')
                print(download_url)
                break
            except Exception as e:
                print(e)

        while True:
            try:
                driver.get(download_url)
                iframe = driver.find_elements('tag name', 'iframe')[0]
                driver.switch_to.frame(iframe)
                download_url = driver.find_element(by=By.XPATH, value='//*[@id="tourl"]/a').get_attribute('href')
                print(download_url)
                return
            except Exception as e:
                src = driver.find_element(by=By.TAG_NAME, value='source').get_attribute('src')
                driver.close()
                with open(f'{songs[index - 1]["title"]}-{songs[index - 1]["singer"]}.mp3', 'wb') as f:
                    f.write(requests.get(src).content)
                    print('下载成功')
                    return


if __name__ == '__main__':
    my_free_mp3 = MyFreeMP3(input('输入歌曲名:'))
    my_free_mp3.download()
