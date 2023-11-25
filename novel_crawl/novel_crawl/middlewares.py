# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import random

import requests
from scrapy import signals
from fake_useragent import UserAgent
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware

import proxy_util


class NovelCrawlSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # 为通过爬虫的每个响应调用
        # 中间件并进入蜘蛛网。

        # 应返回 None 或引发异常。
        return None

    def process_spider_output(self, response, result, spider):
        # 使用从 Spider 返回的结果调用，之后
        # 它已经处理了响应。

        # 必须返回 Request 或 item 对象的可迭代对象。
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # 用爬虫的启动请求调用，并工作
        # 与 process_spider_output（） 方法类似，除了
        # 它没有关联的响应。

        # 必须只返回请求（不返回项目）。
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class NovelCrawlDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self):
        self.s = requests.session()

    @classmethod
    def from_crawler(cls, crawler):
        # Scrapy 使用此方法来创建您的蜘蛛。
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # 为通过下载器的每个请求调用
        # 中间件。

        # 必须：
        # - return None：继续处理此请求
        # - 或者返回一个 Response 对象
        # - 或者返回一个 Request 对象
        # - 或者 raise IgnoreRequest： process_exception（） 方法
        # 安装下载器中间件将被调用
        request.headers['User-Agent'] = UserAgent().random
        return None

    def process_response(self, request, response, spider):
        # 使用下载器返回的响应调用。

        # 必须;
        # - 返回一个 Response 对象
        # - 返回一个 Request 对象
        # - 或引发 IgnoreRequest
        if request.meta.get('dont_retry', False):
            return response

        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            try:
                request.meta['proxy'] = 'https://' + proxy_util.get_random_proxy()
            except requests.exceptions.RequestException:
                print('获取代理ip失败！')
                spider.logger.error('获取代理ip失败！')

            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        # 当下载处理程序或 process_request（） 时调用
        # （来自其他下载器中间件）引发异常。

        # 必须：
        # - return None：继续处理此异常
        # - 返回一个 Response 对象： stops process_exception（） 链
        # - 返回一个 Request 对象： stops process_exception（） chain'

        try:
            request.meta['proxy'] = 'http://' + proxy_util.get_random_proxy()
        except requests.exceptions.RequestException:
            print('***get proxy fail!')
            spider.logger.error('***get proxy fail!')
        return request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
