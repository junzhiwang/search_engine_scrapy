# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import datetime
import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def get_number(value):
    match_re = re.match(r".*?(\d+).*", value)
    if match_re:
        return int(match_re.group(1))
    else:
        return 0


def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value


def date_convert(value):
    try:
        create_date = value.replace("·", "").strip()
        create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
    except Exception:
        create_date = datetime.datetime.now().date()
    return create_date


def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    # Customize item loader
    default_output_processor = TakeFirst()


class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    favorite_number = scrapy.Field(
        input_processor=MapCompose(get_number)
    )
    bookmark_number = scrapy.Field(
        input_processor=MapCompose(get_number)
    )
    comment_number = scrapy.Field(
        input_processor=MapCompose(get_number)
    )
    content = scrapy.Field()
    tag_list = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )

