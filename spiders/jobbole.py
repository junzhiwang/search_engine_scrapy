# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import JobboleArticleItem
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

        article_item = JobboleArticleItem()
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

        title = response.css(".entry-header h1::text").extract()[0]
        create_date = response.css(".entry-meta-hide-on-mobile::text").extract_first("").replace("·", "").strip()
        favorite_number = response.css(".vote-post-up h10::text").extract_first("")
        if favorite_number:
            favorite_number = int(favorite_number)
        else:
            favorite_number = 0

        bookmark_number = response.css(".bookmark-btn::text").extract()[0]
        bookmark_number = re.match(r".*?(\d+).*", bookmark_number)
        if bookmark_number:
            bookmark_number = bookmark_number.group(1)
        else:
            bookmark_number = 0

        comment_number = response.css("a[href='#article-comment'] span::text").extract()[0]
        comment_number = re.match(r".*?(\d+).*", comment_number)
        if comment_number:
            comment_number = comment_number.group(1)
        else:
            comment_number = 0

        content = response.css('div.entry').extract()[0]

        tag_list = response.css('.entry-meta-hide-on-mobile a::text').extract()
        if tag_list:
            tag_list = [tag for tag in tag_list if not tag.strip().endswith("评论")]
        tag_list = ",".join(tag_list)

        print(front_image_url)
        print(title)
        print(create_date)
        print(favorite_number)
        print(bookmark_number)
        print(comment_number)
        # print(content)
        print(tag_list)

        article_item['url_object_id'] = get_md5(response.url)
        article_item['title'] = title
        article_item['url'] = response.url
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        article_item['create_date'] = create_date
        article_item['front_image_url'] = [front_image_url]
        article_item['favorite_number'] = favorite_number
        article_item['bookmark_number'] = bookmark_number
        article_item['comment_number'] = comment_number
        article_item['tag_list'] = tag_list
       # article_item['content'] = content

        yield article_item
        pass

