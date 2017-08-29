# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
import codecs
import json
import pymysql
import pymysql.cursors


class JsonExporterPipeline(object):

    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class JsonWithEncodingPipeline(object):

    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self):
        self.file.close()


class MysqlPipeline(object):

    def __init__(self):
        self.connect = pymysql.connect('localhost', 'root', '', 'article_spider', charset='utf8mb4', use_unicode=True)
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article(url_object_id, title, url, create_date, front_image_url, front_image_path,
                                favorite_number, bookmark_number, comment_number, tag_list, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item['url_object_id'], item['title'], item['url'], item['create_date'],
                                         item['front_image_url'], item['front_image_path'], item['favorite_number'],
                                         item['bookmark_number'], item['comment_number'], item['tag_list'],
                                         item['content']))
        self.connect.commit()
        return item


class MysqlTwistedPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("pymysql", **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        # Make mysql insertion async method using twisted
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)
        return item

    def handle_error(self, failure):
        # handle aysnc insertion exceptions
        print(failure)

    def do_insert(self, cursor, item):
        # Execute insertion
        insert_sql = """
          insert into article(url_object_id, title, url, create_date, front_image_url, front_image_path,
                            favorite_number, bookmark_number, comment_number, tag_list, content)
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (item['url_object_id'], item['title'], item['url'], item['create_date'],
                                    item['front_image_url'], item['front_image_path'], item['favorite_number'],
                                    item['bookmark_number'], item['comment_number'], item['tag_list'],
                                    item['content']))


class ArticleImagePipeline(ImagesPipeline):

    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item
