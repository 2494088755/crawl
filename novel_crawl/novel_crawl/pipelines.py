# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd


class OneSevenKPipeline:
    def __init__(self):
        self.data = []

    def open_spider(self, spider):
        pass
        # self.f = open("17k.txt", "w", encoding="utf-8")

    def process_item(self, item, spider):
        # self.f.write(f"{item['type_']}\t{item['book_name']}\t{item['author']}\t{item['number']}\n")
        # self.f = self.f.append(item, ignore_index=True)
        if spider.name == "17k":
            self.data.append(item)
        return item

    def close_spider(self, spider):
        if spider.name == "17k":
            # self.f.close()
            df = pd.DataFrame(self.data)
            # pandas.read_csv() 函数的常用参数如下。
            # filepath_or_buffer：文件路径或类文件对象，指定要读取的 CSV 文件的位置或 URL。
            # sep/delimiter：指定字段之间的分隔符，默认为逗号 ,。你可以使用这个参数来指定其他分隔符，比如制表符 \t 等。
            # header：用作列名的行号，默认为 0（第一行）。如果没有列名，可以设置为 None。
            # index_col：用作行索引的列编号或列名。可以是单个列名/编号或列名/编号的列表（多级索引）。
            # usecols：指定要读取的列，可以是列名/列编号的列表或函数。默认情况下，读取所有列。
            # dtype：指定每列的数据类型。可以是字典（列名与数据类型的映射），也可以是单个数据类型，比如 dtype='str'。
            # parse_dates：将指定列解析为日期格式。可以是布尔值（解析所有日期列），也可以是列名/列编号的列表。
            # na_values：指定哪些值应该被视为缺失值。可以是列表、字符串或字典。
            # skiprows/skipfooter：跳过文件开头或结尾的行数，用于忽略标题或尾部的注释行等。
            # nrows：读取文件的行数，从文件开头算起。
            # chunksize：一次性读取文件的行数，返回一个迭代器。
            # encoding：指定文件编码格式，比如 'utf-8'、'latin1' 等。
            df.to_csv("17k.csv", sep="\t", index=False)
        # pass


class DingDianPipeline:
    def __init__(self):
        self.data = []

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        if spider.name == "dingdian":
            self.data.append(item)
        return item

    def close_spider(self, spider):
        if spider.name == "dingdian":
            df = pd.DataFrame(self.data)
            df.to_csv("dingdian.csv", sep="\t", index=False)
