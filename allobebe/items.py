# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AllobebeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    url_origin = scrapy.Field()
    status = scrapy.Field()
    title = scrapy.Field()
    discount_price = scrapy.Field()
    former_price = scrapy.Field()
    prop_rating = scrapy.Field()
    prop_reviews = scrapy.Field()
    prop_image_1 = scrapy.Field()
    prop_image_2 = scrapy.Field()
    prop_image_3 = scrapy.Field()
    description = scrapy.Field()
    classification = scrapy.Field()
    prop_brand = scrapy.Field()
    prop_color = scrapy.Field()
    prop_size = scrapy.Field()
    
