import scrapy

from ..items import OneSevenKItem


class OneSevenKSpider(scrapy.Spider):
    name = "17k"
    allowed_domains = ["www.17k.com"]
    # start_urls = ["https://www.17k.com"]
    start_urls = ["https://www.17k.com/all/book/2_0_0_0_0_0_0_0_1.html"]
    page = 1

    def parse(self, response):
        print(f"当前页码: {self.page}")

        trs = response.xpath('/html/body/div[4]/div[3]/div[2]/table/tbody/tr')
        for tr in trs[1:]:
            type_ = tr.xpath('./td[2]/a/text()').extract_first()
            book_name = tr.xpath('./td[3]/span/a/text()').extract_first()
            number = tr.xpath('./td[5]/text()').extract_first()
            author = tr.xpath('./td[6]/a/text()').extract_first()
            status = str(tr.xpath('./td[8]/em/text()').extract_first()).replace('\n', '').replace('\r', '').replace(' ',
                                                                                                                    '')
            item = OneSevenKItem(type_=type_, book_name=book_name, author=author, number=number, status=status)
            yield item

        if self.page < 10:
            self.page += 1
        url = f"https://www.17k.com/all/book/2_0_0_0_0_0_0_0_{self.page}.html"
        yield scrapy.Request(url=url, callback=self.parse)

