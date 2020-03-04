# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"

class ReviewItem(scrapy.Item):
    ratings = scrapy.Field()
    names = scrapy.Field()
    reviewdates = scrapy.Field()
    reviews = scrapy.Field()

class MiscInfoItem(scrapy.Item):
    num_reviews = scrapy.Field()

class NoItem(scrapy.Item):
    pass