# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FoodyItem(scrapy.Item):

    # general
    name = scrapy.Field()

    avgRating = scrapy.Field()
    detailRating = scrapy.Field()
    hasBooking = scrapy.Field()
    hasDelivery = scrapy.Field()

    address = scrapy.Field()
    district = scrapy.Field()
    city = scrapy.Field()
    phone = scrapy.Field()

    open_time = scrapy.Field()
    price_range = scrapy.Field()

    totalReview = scrapy.Field()
    totalView = scrapy.Field()
    totalFavourite = scrapy.Field()
    totalCheckins = scrapy.Field()

    categories = scrapy.Field()
    reviewUrl = scrapy.Field()
    albumUrl = scrapy.Field()

    reviews = scrapy.Field()
    photos = scrapy.Field()
    # videos = scrapy.Field() 