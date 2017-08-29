# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from scrapy.loader import ItemLoader
from ArticleSpider.items import JobboleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. Parse all article urls
        2. extract next page's url and handover it to scrapy
        :param response:
        :return:
        """
        # Parse all article urls and handover it to parse
        post_nodes = response.css("#archive .post.floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url}, callback=self.parse_detail)
            print(post_url)

        # Extract next page's url and handover it to scrapy
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):

        front_image_url = response.meta.get("front_image_url", "")
        """
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]

        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace("·", "").strip()

        favorite_number = int(response.xpath('//h10[contains(@id, "votetotal")]/text()').extract()[0])

        bookmark_number = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract()[0]
        if bookmark_number:
            bookmark_number = int(re.match(r".*?(\d+).*", bookmark_number).group(1))

        comment_number = response.xpath('//a[@href="#article-comment"]/text()').extract()[0]
        if comment_number:
            comment_number = int(re.match(r".*?(\d+).*", comment_number).group(1))

        content = response.xpath('//div[@class="entry"]').extract()[0]

        tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        if tag_list:
            tag_list = [tag for tag in tag_list if not tag.strip().endswith("评论")]
        """

        # Load items using ItemLoader
        item_loader = ArticleItemLoader(item=JobboleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("create_date", ".entry-meta-hide-on-mobile::text")
        item_loader.add_css("favorite_number", ".vote-post-up h10::text")
        item_loader.add_css("bookmark_number", ".bookmark-btn::text")
        item_loader.add_css("comment_number", "a[href='#article-comment'] span::text")
        item_loader.add_css("tag_list", ".entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")

        article_item = item_loader.load_item()
        yield article_item
        pass

