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
import re
from scrapy.exceptions import CloseSpider

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
        for lista in data_json:
            for key,value in lista.items():
                if key == 'link':
                    if base_url in value and bandera:
                        print("link",value)
                        last_new = value
                        bandera = False
        return last_new
    
    else:
        return last_new


class cryptonomist(scrapy.Spider):
    name = 'cryptonomist'
    base_url = 'https://cryptonomist.ch'
    last_new = ''
    custom_settings = {'LOG_LEVEL': 'INFO'}        # funciona para visualizar los items scrapeando
    
    # Aux
    contador = 0
    flag = False
    all_pages = 1

    def __init__(self, *args, **kwargs):
        self.schedule = kwargs.pop('schedule', '')  # path to where all workflows are stored
        
    def start_requests(self):
        urls = [
            'https://cryptonomist.ch',
            #'https://en.cryptonomist.ch'
        ]
        for url in urls:
            self.last_new = Last_New(url)
            yield Request(url=url, callback=self.start_search, dont_filter=True)

    def start_url(self,response):
        if self.contador < self.all_pages:
            yield Request(url=response.url, callback=self.start_search, dont_filter=True)
        else:
            raise CloseSpider('Ultima pagina de scrapy')

    def start_search(self, response):
        news = response.xpath('//div[contains(@class, "latest-posts")]/div[contains(@class, "post")]')
        for n in news:
            fecha = n.xpath('.//span[contains(@class, "time")]/text()').extract_first()
            title = n.xpath('.//h4[contains(@class, "post-title")]/text()').extract_first()
            descripcion = n.xpath('.//p[contains(@class, "post-description m-t-20")]/text()').extract_first()
            link = n.xpath('.//div[contains(@class, "post-content")]/a/@href').extract_first()
            link_image = n.xpath('.//img[contains(@loading, "lazy")]/@src').extract_first()
            author = n.xpath('.//p[contains(@class, "author")]/a/text()').extract_first()
            link_author = n.xpath('.//p[contains(@class, "author")]/a/@href').extract_first()
            
            #Convierte la fecha en formato YYYY-MM-DD
            if fecha:
                # convertir la fecha en ingles
                date = Translator().translate(str(fecha.replace('-','').replace('Lug','Jul'))).text
                organizar_date = date.split()
                organizar_date[0] = organizar_date[0] + ','
                date = organizar_date[1] +' '+ organizar_date[0] +' '+organizar_date[2]

            # Guardar los datos
            if link == self.last_new:
                print("ultimoScrapy",link)
                self.flag = True

            item = NoticiasItem()
            #Convierte la fecha en formato YYYY-MM-DD
            date = time_format(date.strip())
            item['date'] = date
            item['title'] = title
            item['description'] = descripcion
            item['link'] = link
            item['history'] = str(self.schedule)
            item['image'] = link_image
            item['author'] = author
            item['link_author'] = link_author
            item['dominio'] = self.base_url
            item['views'] = 0
            
            # News Body
            if link is not None:
                yield scrapy.Request(url=link, callback = self.parse_information, meta={'same_item':item})

            else:
                language = response.xpath('/html/@lang').extract_first()
                item['language'] = language
                item['category'] = 'Crypto'
                item['news_body'] = ''
                yield item
            
        # Btn-Next
        if self.contador == 0:
            num_pages = response.xpath('//a[contains(@class, "page-numbers")]/text()').getall()
            print(num_pages[1],"num_pages",num_pages)
            self.all_pages = int(num_pages[1].replace(',',''))
        
        # Verifica si encontro la ultima noticia en esa pagina
        if self.flag:
            raise CloseSpider('Encontro la ultima scrapy')

        next_url = response.xpath('//a[contains(@class, "next page-numbers")]/@href').get()
        print("NEXT",next_url)
        self.contador += 1
        yield Request(url=next_url, callback=self.start_url, dont_filter=True)

    def parse_information(self, response):
        data_extended = response.meta.get('same_item')
        category = response.xpath('//div[contains(@class, "content")]/span[contains(@class, "category")]/text()').extract_first()
        language = response.xpath('/html/@lang').extract_first()
        body = response.xpath('//div[contains(@class, "post-content qnxp-post")]/p|//div[contains(@class, "post-content qnxp-post")]/blockquote/p/span/i/span').getall()
        
        # Limpiar HTML
        for i,d in enumerate(body[:5]):
            body[i] = re.sub('(<([^>]+)>)', '', d)

        # Guardar
        data_extended['category'] = category
        data_extended['news_body'] = body[:5]
        data_extended['language'] = language
        yield data_extended

    def open_page(self, response): #Funcion para hacer pruebas
        print("texto",response.text)
        open_in_browser(response)