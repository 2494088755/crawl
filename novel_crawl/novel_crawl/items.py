# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OneSevenKItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    type_ = scrapy.Field()
    book_name = scrapy.Field()
    author = scrapy.Field()
    number = scrapy.Field()
    status = scrapy.Field()


class DingDianItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    type_ = scrapy.Field()
    name = scrapy.Field()
    latest_chapters = scrapy.Field()
    author = scrapy.Field()
    count = scrapy.Field()
    status = scrapy.Field()
    update_time = scrapy.Field()
