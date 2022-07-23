# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FoodyItem(scrapy.Item):

    # general
    name = scrapy.Field()
    shop_type = scrapy.Field()
    category = scrapy.Field()
    address = scrapy.Field()
    open_time = scrapy.Field()
    price_range = scrapy.Field()

    # menu
    menu = scrapy.Field()

    # review
    reviews = scrapy.Field()

    # gallery
    photos = scrapy.Field()
    # videos = scrapy.Field() 

    # # rating
    # detail_rating = scrapy.Field()
    # avg_rating = scrapy.Field()
    
