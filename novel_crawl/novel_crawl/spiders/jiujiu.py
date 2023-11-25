import scrapy


class JiujiuSpider(scrapy.Spider):
    name = "jiujiu"
    allowed_domains = ["www.jjxsxs.com"]
    page = 1
    start_urls = [f'https://fanqienovel.com/library/all/page_{page}?sort=hottes']

    def parse(self, response):
        print(f"当前页码: {self.page}")
        book_list = response.xpath('//*[@class="stack-book-item"]')
        for book in book_list:
            book_name = book.xpath('./div[2]/div[1]/a/text()').extract_first()
            print(book_name)
