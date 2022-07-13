# -*- coding: utf-8 -*-
import scrapy
import string
import json 
from datetime import datetime
from scrapy import Request
from scrapy.utils.response import open_in_browser
from noticias.items import NoticiasItem
from noticias.Time_format import time_format
from scrapy.selector import Selector
from googletrans import Translator
from scrapy import FormRequest
from scrapy.http import JsonRequest
from scrapy.http import HtmlResponse
from scrapy.exceptions import CloseSpider
import re

def Last_New(base_url):
    import json
    import os
    from os import path
    
    last_new = ''
    path_folder = (os.getcwd()).replace('BackCryptoNews/noticias','') + 'data/'
    # Windows SO
    # path_folder = (os.getcwd()).replace('\\BackCryptoNews\\noticias','') + '\\data/'

    name_json = 'items'
    workname = name_json + '.json'
    bandera = True

    # Ultimo en data
    if os.path.exists(path.join(path_folder, workname)):
        with open(path.join(path_folder, workname)) as file:
            data_json = json.load(file)

        # Buscar el ultima noticia scrapiada en cada dominio
        cont = 0
        for lista in data_json:
            for i,(key,value) in enumerate(lista.items()):
                if key == 'dominio':
                    cont += 1
                    if base_url in value and bandera:
                        print(cont,"Dominio:",value)
                        print("data_json[0]:",data_json[cont]['link'])
                        last_new = data_json[cont]['link']
                        bandera = False
        return last_new
    
    else:
        return last_new



class watcher_guru(scrapy.Spider):
    name = 'watcher_guru'
    base_url = 'https://watcher.guru'
    last_new = Last_New(base_url)
    custom_settings = {'LOG_LEVEL': 'INFO'}        # funciona para visualizar los items scrapeando
    
    # Aux
    page = 2
    flag = False
    language = ''
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

    def __init__(self, *args, **kwargs):
        self.schedule = kwargs.pop('schedule', '')  # path to where all workflows are stored
        #print("self.schedule",self.schedule)
        
    def start_requests(self):
        urls = [
            'https://watcher.guru/news/?c=1'
        ]

        for url in urls:
            yield Request(url=url, callback=self.start_search)

    
    def start_search(self, response):
        print("--------------------------")
        print("self.last_new",self.last_new)
        print("--------------------------")

        if self.page == 2:
            # Buscar noticias de la pagina
            news = response.xpath('//div[contains(@class, "cs-posts-area__main cs-archive-standard-type-1")]/article')
            for n in news:
                link_image = n.xpath('.//div[contains(@class, "cs-entry__outer")]/div[contains(@class, "cs-entry__inner cs-entry__thumbnail")]/div/img/@data-src-img').extract_first()
                category = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__post-meta")]/div/ul/li/a/text()').extract_first()
                title = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/h2[contains(@class, "cs-entry__title")]/a/text()').extract_first()
                link = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/h2[contains(@class, "cs-entry__title")]/a/@href').extract_first()
                descripcion = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__excerpt")]/text()').extract_first()
                fecha = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__details")]/div/div/div/div/text()').extract_first()
                author = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__details")]/div/div/div/a/text()').extract_first()
                link_author = n.xpath('.//div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__details")]/div/div/div/a/@href').extract_first()
                language = response.xpath('/html/@lang').extract_first()
                
                # Guardar los datos
                if link == self.last_new:
                    print("ultimoScrapy",link)
                    self.flag = True

                item = NoticiasItem()

                if fecha:
                    fecha_split = fecha.split()
                    for clave in self.array_moth:
                        if clave == fecha_split[0]:
                            fecha_split[0] = self.array_moth[clave]

                    fecha = '{} {} {}'.format(fecha_split[0],fecha_split[1],fecha_split[2])
                    date = time_format(fecha.strip())
                
                if author:
                    print("title",title)
                    item['date'] = date
                    item['title'] = title
                    item['description'] = descripcion
                    item['link'] = link
                    item['category'] = category
                    item['image'] = link_image
                    item['author'] = author
                    item['link_author'] = link_author
                    item['dominio'] = self.base_url
                    self.language = language
                    item['language'] = language
                    item['views'] = 0
                    item['history'] = str(self.schedule)
                
                    # News Body
                    if link is not None:
                        yield scrapy.Request(url=link, callback = self.parse_information, meta={'same_item':item})

                    else:
                        item['news_body'] = ''
                        yield item

                # Verifica si encontro la ultima noticia en esa pagina
                if self.flag:
                    raise CloseSpider('Encontro la ultima scrapy')

                # Btn-Next
                params = {
                    'action': 'csco_ajax_load_more',
                    'page': str(self.page),
                    'posts_per_page': '10',
                    'attributes': 'false',
                    '_ajax_nonce': 'ef1dcc01a1',
                    'options': '{"location":"archive","meta":"archive_post_meta","layout":"list","columns":2,"compact_meta":true,"image_orientation":"original","image_size":"csco-thumbnail","image_width":"half","overlay_image":false,"more_button":true,"summary_type":"summary"}',
                }
                
                yield FormRequest(
                        url = 'https://watcher.guru/news/wp-json/csco/v1/more-posts',
                        formdata = params,
                        method='POST',
                        callback = self.paginacion
                )


    def paginacion(self, response):
        print("NEXT",self.page)
        data = response.json()
        body = data['data']['content']

        link_image = Selector(text=body).xpath('//article/div[contains(@class, "cs-entry__outer")]/div[contains(@class, "cs-entry__inner")]/div[contains(@class, "cs-overlay-background")]/img[contains(@class, "attachment-csco-thumbnail")]/@src').getall()
        category = Selector(text=body).xpath('//article/div/div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__post-meta")]/div/ul/li/a/text()').getall()
        title = Selector(text=body).xpath('//article/div/div[contains(@class, "cs-entry__inner cs-entry__content")]/h2[contains(@class, "cs-entry__title")]/a/text()').getall()
        link = Selector(text=body).xpath('//article/div/div[contains(@class, "cs-entry__inner cs-entry__content")]/h2[contains(@class, "cs-entry__title")]/a/@href').getall()
        descripcion = Selector(text=body).xpath('//article/div/div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__excerpt")]/text()').getall()
        fecha = Selector(text=body).xpath('//div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__details")]/div/div/div/div/text()').getall()
        author = Selector(text=body).xpath('//article/div/div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__details")]/div/div/div/a/text()').getall()
        link_author = Selector(text=body).xpath('//article/div/div[contains(@class, "cs-entry__inner cs-entry__content")]/div[contains(@class, "cs-entry__details")]/div/div/div/a/@href').getall()
        
        for i,d in enumerate(title):

            # Guardar los datos
            if link == self.last_new:
                print("ultimoScrapy",link)
                self.flag = True

            item = NoticiasItem()

            if fecha[i]:
                fecha_split = fecha[i].split()
                for clave in self.array_moth:
                    if clave == fecha_split[0]:
                        fecha_split[0] = self.array_moth[clave]

                fecha_nueva = '{} {} {}'.format(fecha_split[0],fecha_split[1],fecha_split[2])
                date = time_format(fecha_nueva.strip())

            item['date'] = date
            item['title'] = title[i]
            item['description'] = descripcion[i]
            item['link'] = link[i]
            item['category'] = category[i]
            item['image'] = link_image[i]
            item['author'] = author[i]
            item['link_author'] = link_author[i]
            item['dominio'] = self.base_url
            item['language'] = self.language
            item['views'] = 0
            item['history'] = str(self.schedule)
            
            # News Body
            if link is not None:
                yield scrapy.Request(url=link[i], callback = self.parse_information, meta={'same_item':item})

            else:
                item['news_body'] = ''
                yield item

        self.page += 1

        # Verifica si encontro la ultima noticia en esa pagina
        if self.flag:
            raise CloseSpider('Encontro la ultima scrapy')


        if self.page <= 5:
            # Btn-Next
            params = {
                'action': 'csco_ajax_load_more',
                'page': str(self.page),
                'posts_per_page': '100',
                'attributes': 'false',
                '_ajax_nonce': 'ef1dcc01a1',
                'options': '{"location":"archive","meta":"archive_post_meta","layout":"list","columns":2,"compact_meta":true,"image_orientation":"original","image_size":"csco-thumbnail","image_width":"half","overlay_image":false,"more_button":true,"summary_type":"summary"}',
            }
            
            yield FormRequest(
                    url = 'https://watcher.guru/news/wp-json/csco/v1/more-posts',
                    formdata = params,
                    method='POST',
                    callback = self.paginacion
            )
        
    def parse_information(self, response):
        data_extended = response.meta.get('same_item')
        body = response.xpath('//div[contains(@class, "entry-content")]/p').getall()
        #print(len(body),"body",body)
        for i,d in enumerate(body[:5]):
            body[i] = re.sub('(<([^>]+)>)', '', d)
            #print("list_body[i]",body[i])
        data_extended['news_body'] = body[:5]
        yield data_extended
    
    
    def open_page(self, response): #Funcion para hacer pruebas
        print("texto",response.text)
        open_in_browser(response)