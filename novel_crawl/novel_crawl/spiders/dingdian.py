import scrapy
from bs4 import BeautifulSoup

from ..items import DingDianItem


class DingDianSpider(scrapy.Spider):
    name = "dingdian"
    allowed_domains = ["www.xindingdianxsw.net.com"]
    page = 1
    start_urls = [f'https://www.xindingdianxsw.net/top/allvisit_{page}.html']
    handle_httpstatus_list = [403]

    def start_requests(self):
        headers = {
            'Cookie': 'waf_sc=5889647726; __duid=2_fcbe15baae4c95c341425f51ab4bd6e41666175281578; sex=boy; '
                      'Hm_lvt_96eba8bd393f2a0d8fbbfe04c14fc62a=1700918653; novel_38373=17516175%7C1700920130; '
                      'Hm_lpvt_96eba8bd393f2a0d8fbbfe04c14fc62a=1700921624 '
        }
        yield scrapy.Request(url=self.start_urls[0], headers=headers)


    def parse(self, response):
        print(f"当前页码: {self.page}")
        soup = BeautifulSoup(response.text, 'html.parser')
        ul = soup.find('div', class_='novelslist2')
        li_list = ul.find_all('li')
        for li in li_list[1:]:
            type_ = li.find('span', class_='s1')
            try:
                name = li.find('span', class_='s2 boys').text
            except Exception as e:
                name = li.find('span', class_='s2 girls').text
            latest_chapters = li.find('span', class_='s3')
            author = li.find('span', class_='s4')
            count = li.find('span', class_='s5')
            status = li.find('span', class_='s6')
            update_time = li.find('span', class_='s7')
            item = DingDianItem(type_=type_.text, name=name, latest_chapters=latest_chapters.text,
                                author=author.text, count=count.text, status=status.text, update_time=update_time.text)
            yield item

        if self.page < 5:
            self.page += 1
            yield scrapy.Request(url=f'https://www.xindingdianxsw.net/top/allvisit_{self.page}.html',
                                 callback=self.parse, dont_filter=True)
