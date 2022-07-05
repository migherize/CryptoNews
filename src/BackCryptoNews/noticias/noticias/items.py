# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class NoticiasItem(scrapy.Item):
    # define the fields for your item here like:
    date = scrapy.Field()
    title = scrapy.Field()
    category = scrapy.Field()
    author = scrapy.Field()
    image = scrapy.Field()
    description = scrapy.Field()
    language = scrapy.Field()
    history = scrapy.Field()    
    dominio = scrapy.Field()
    link = scrapy.Field()
    link_author = scrapy.Field()
    news_body = scrapy.Field()
    views = scrapy.Field()
    pass
