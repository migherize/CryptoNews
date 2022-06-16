# -*- coding: utf-8 -*-
import scrapy
import string
import json 
from datetime import datetime
from scrapy import Request
from scrapy.utils.response import open_in_browser
from noticias.items import NoticiasItem
from noticias.time import time
from googletrans import Translator

def clean_text(text, replace_commas_for_spaces=True):
    text = str(text)
    if not isinstance(text, float) and not isinstance(text, int):
        text = ''.join([c for c in text if c in string.printable])
        if replace_commas_for_spaces:
            text = text.replace(';', ' ').replace(',', '').replace('"','').replace("['", '').replace("']", '').replace('\xa0','')\
                .replace("\n", '').replace("\t", '').replace("\r", '').strip()
        else:
            text = text.replace(';', ' ').replace(',', '').replace('"','').replace("['", '').replace("']", '').replace('\xa0','').replace("\n", '').strip()
    if text == 'nan':
        text = ''
    return text


class cryptonomist(scrapy.Spider):
    name = 'cryptonomist'
    
    def __init__(self, *args, **kwargs):
        self.schedule = kwargs.pop('schedule', '')  # path to where all workflows are stored
        #print("self.schedule",self.schedule)
        
    def start_requests(self):
        url = 'https://cryptonomist.ch/'
        yield Request(url=url, callback=self.start_search, dont_filter=True)

    def start_search(self, response):
        #print("url",response.url)
        news = response.xpath('//div[contains(@class, "latest-posts")]/div[contains(@class, "post")]')
        #print("noticas",len(news))
        for n in news:
            #ert = n.xpath('.//span[contains(@class, "ert")]/text()').extract_first()
            fecha = n.xpath('.//span[contains(@class, "time")]/text()').extract_first()
            title = n.xpath('//h4[contains(@class, "post-title")]/text()').extract_first()
            descripcion = n.xpath('.//p[contains(@class, "post-description m-t-20")]/text()').extract_first()
            link = n.xpath('.//div[contains(@class, "post-content")]/a/@href').extract_first()
            link_image = n.xpath('.//img[contains(@loading, "lazy")]/@src').extract_first()

            # convertir la fecha en ingles
            date = Translator().translate(str(fecha.replace('-',''))).text
            organizar_date = date.split()
            organizar_date[0] = organizar_date[0] + ','
            date = organizar_date[1] +' '+ organizar_date[0] +' '+organizar_date[2]

            # Guardar los datos
            item = NoticiasItem()
            date = time(date.strip())
            item['date'] = date
            item['title'] = clean_text(title)
            item['description'] = clean_text(descripcion)
            item['link'] = link
            item['history'] = str(self.schedule)
            item['language'] = 'it'
            item['category'] = 'Crypto'
            item['image'] = link_image
            
            print("item_spider",item)
            yield item

    def open_page(self, response): #Funcion para hacer pruebas
        print("texto",response.text)
        open_in_browser(response)