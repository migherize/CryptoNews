# -*- coding: utf-8 -*-
import scrapy
import string
import json 
from datetime import datetime
from scrapy import Request
from scrapy.utils.response import open_in_browser
from noticias.items import NoticiasItem
from noticias.Time_format import time_format
from scrapy import Selector
from googletrans import Translator
from scrapy import FormRequest
from scrapy.http import JsonRequest
import re

class coin(scrapy.Spider):
    name = 'coin'
    base_url = 'https://watcher.guru'
    #custom_settings = {'LOG_LEVEL': 'INFO'}        # funciona para visualizar los items scrapeando
    
    def __init__(self, *args, **kwargs):
        self.schedule = kwargs.pop('schedule', '')  # path to where all workflows are stored
        #print("self.schedule",self.schedule)
        
    def start_requests(self):
        urls = [
            'https://coinmarketcap.com/alexandria/categories/market-musing',
        ]
        for url in urls:
            yield Request(url=url, callback=self.open_page, dont_filter=True)

    def start_search(self, response):
        #print("url",response.url)
        news = response.xpath('//div[contains(@class, "cs-posts-area__main")]/article')
        #print("noticas",len(news))
        for n in news:
            link_image = n.xpath('.//div[contains(@class, "cs-entry__outer")]/div[contains(@class, "cs-entry__inner")]/div[contains(@class, "cs-overlay-background")]/img[contains(@class, "attachment-csco-thumbnail")]/@data-lazy-src').extract_first()
            category = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__post-meta")]/div/ul/li/a/text()').extract_first()
            title = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/h2[contains(@class, "cs-entry__title")]/a/text()').extract_first()
            link = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/h2[contains(@class, "cs-entry__title")]/a/@href').extract_first()
            descripcion = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__excerpt")]/text()').extract_first()
            fecha = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__details")]/div/div/div/div/text()').extract_first()
            author = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__details")]/div/div/div/a/text()').extract_first()
            link_author = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__details")]/div/div/div/a/@href').extract_first()
            language = response.xpath('/html/@lang').extract_first()

            array_moth = {
                'January':'Jan', 
                'February':'Feb', 
                'March':'Mar', 
                'April':'Apr', 
                'May':'May', 
                'June':'Jun',
                'July':'Jul', 
                'August':'Aug', 
                'September':'Sep', 
                'Octuber':'Oct', 
                'November':'Nov', 
                'December':'Dec'
            }

            # Guardar los datos
            item = NoticiasItem()

            if fecha:
                fecha_split = fecha.split()
                for clave in array_moth:
                    if clave == fecha_split[0]:
                        fecha_split[0] = array_moth[clave]

                fecha = '{} {} {}'.format(fecha_split[0],fecha_split[1],fecha_split[2])
                date = time_format(fecha.strip())
            
            if author:
                item['date'] = date
                item['title'] = title
                item['description'] = descripcion
                item['link'] = link
                item['category'] = category
                item['image'] = link_image
                item['author'] = author
                item['link_author'] = link_author
                item['dominio'] = self.base_url
                item['language'] = language
                item['views'] = 0
                item['history'] = str(self.schedule)
            
                # News Body
                if link is not None:
                    yield scrapy.Request(url=link, callback = self.parse_information, meta={'same_item':item})

                else:
                    item['news_body'] = ''
                    yield item
        # Btn-Next
        next_url = response.xpath('//div[contains(@class, "cs-posts-area__pagination")]').getall()
        print("NEXT",next_url)
        '''
        #yield Request(url=next_url, callback=self.start_url, dont_filter=True)
        params = {
            'action': 'csco_ajax_load_more',
            'page': '2',
            'posts_per_page': '10',
            'attributes': 'false',
            '_ajax_nonce': 'ef1dcc01a1',
            'options': '{"location":"archive","meta":"archive_post_meta","layout":"list","columns":2,"compact_meta":true,"image_orientation":"original","image_size":"csco-thumbnail","image_width":"half","overlay_image":false,"more_button":true,"summary_type":"summary"}',
            'query_data': '{"first_post_count":10,"infinite_load":false,"query_vars":{"category_name":"bitcoin","error":"","m":"","p":0,"post_parent":"","subpost":"","subpost_id":"","attachment":"","attachment_id":0,"name":"","pagename":"","page_id":0,"second":"","minute":"","hour":"","day":0,"monthnum":0,"year":0,"w":0,"tag":"","cat":4,"tag_id":"","author":"","author_name":"","feed":"","tb":"","paged":0,"meta_key":"","meta_value":"","preview":"","s":"","sentence":"","title":"","fields":"","menu_order":"","embed":"","category__in":[],"category__not_in":[],"category__and":[],"post__in":[],"post__not_in":[],"post_name__in":[],"tag__in":[],"tag__not_in":[],"tag__and":[],"tag_slug__in":[],"tag_slug__and":[],"post_parent__in":[],"post_parent__not_in":[],"author__in":[],"author__not_in":[],"ignore_sticky_posts":false,"suppress_filters":false,"cache_results":true,"update_post_term_cache":true,"lazy_load_term_meta":true,"update_post_meta_cache":true,"post_type":"","posts_per_page":10,"nopaging":false,"comments_per_page":"50","no_found_rows":false,"order":"DESC"},"in_the_loop":false,"is_single":false,"is_page":false,"is_archive":true,"is_author":false,"is_category":true,"is_tag":false,"is_tax":false,"is_home":false,"is_singular":false}',
        }

        yield JsonRequest(
                url = 'https://watcher.guru/news/wp-json/csco/v1/more-posts',
                data = params,
                method='POST',
                callback = self.open_page
            )
        '''

    def parse_information(self, response):
        data_extended = response.meta.get('same_item')
        body = response.xpath('//div[contains(@class, "entry-content")]/p').getall()
        print(len(body),"body",body)
        for i,d in enumerate(body[:5]):
            body[i] = re.sub('(<([^>]+)>)', '', d)
            print("list_body[i]",body[i])
        data_extended['news_body'] = body[:5]
        yield data_extended

    def open_page(self, response): #Funcion para hacer pruebas
        print("entre")
        #print("texto",response.text)
        open_in_browser(response)