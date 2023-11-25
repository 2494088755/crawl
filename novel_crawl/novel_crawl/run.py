from scrapy import cmdline

# cmdline.execute("scrapy crawl jiujiu".split())
# cmdline.execute("scrapy crawl 17k".split())
# cmdline.execute("scrapy crawl dingdian".split())
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

crawler = CrawlerProcess(settings)

# crawler.crawl('17k')
crawler.crawl('dingdian')

# crawler.start()
crawler.start()
