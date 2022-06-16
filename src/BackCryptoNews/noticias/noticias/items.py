# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NoticiasItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    history = scrapy.Field()    
    title = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    date = scrapy.Field()
    language = scrapy.Field()
    category = scrapy.Field()
    image = scrapy.Field()
    pass
