import scrapy
import string
import json 
from datetime import date, datetime
from scrapy import Request
from scrapy.utils.response import open_in_browser
from noticias.items import NoticiasItem
from noticias.Time_format import time_format
from scrapy.exceptions import CloseSpider
from scrapy import Selector
from googletrans import Translator
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

class yahoo(scrapy.Spider):
    name = 'yahoo'
    base_url = 'https://finance.yahoo.com'
    last_new = Last_New(base_url)
    contador = 0
    #custom_settings = {'LOG_LEVEL': 'INFO'}        # funciona para visualizar los items scrapeando

    # Aux
    page = 0
    flag = False

    def _init_(self, *args, **kwargs):
        self.schedule = kwargs.pop('schedule', '')  # path to where all workflows are stored
        
    def start_requests(self):
        urls = ['https://finance.yahoo.com/topic/crypto/']
        for url in urls:
            yield Request(url=url, callback=self.start_search, dont_filter=True)
            
    def start_url(self,response):
        print("url",response.url)
        if self.contador < 3:
            yield Request(url=response.url, callback=self.start_search, dont_filter=True)

    def start_search(self, response):
        news = response.xpath('//div[@id="Fin-Stream"]/ul[@class="My(0) P(0) Wow(bw) Ov(h)"]/li[contains(@class, "Pos(r)")]/div/div')
        print("noticas",len(news))
        
        for n in news:
            title = n.xpath('.//div[contains(@class, "Ov(h) Pend(44px) Pstart(25px)")]/h3[contains(@class, "Mb(5px)")]/a/text()').extract_first()
            descripcion = n.xpath('.//div[contains(@class, "Ov(h) Pend(44px) Pstart(25px)")]/p[@class="Fz(14px) Lh(19px) Fz(13px)--sm1024 Lh(17px)--sm1024 LineClamp(2,38px) LineClamp(2,34px)--sm1024 M(0)"]/text()').extract_first()
            link = n.xpath('.//div[@class="Ov(h) Pend(44px) Pstart(25px)"]/h3/a/@href').extract_first()
            link_image = n.xpath('.//div[contains(@class, "Fl(start) Pos(r)")]/div/img/@src').extract_first()
            #link_author = n.xpath('.//p[contains(@class, "author")]/a/@href').extract_first()
            
            # Guardar los datos
            item = NoticiasItem()
            item['title'] = title
            item['description'] = descripcion
            item['link'] = self.base_url + str(link)
            item['history'] = str(self.schedule)
            item['image'] = link_image
            item['dominio'] = self.base_url
            item['views'] = 0
            
            # News Body
            if link is not None:
                yield scrapy.Request(url= self.base_url + link, callback = self.parse_information, meta={'same_item':item})

            else:
                language = response.xpath('/html/@lang').extract_first()
                item['language'] = language
                item['date'] = ''
                item['author'] = ''
                item['link_author'] = ''
                item['category'] = ''
                item['news_body'] = ''
                yield item
            
        # Btn-Next
        #next_url = response.xpath('//a[contains(@class, "next page-numbers")]/@href').get()
        #print("NEXT",next_url)
        #self.contador += 1
        #yield Request(url=next_url, callback=self.start_url, dont_filter=True)

    def parse_information(self, response):
        data_extended = response.meta.get('same_item')
        language = response.xpath('/html/@lang').extract_first()
        
        date = response.xpath('.//div[contains(@class, "caas-attr-time-style")]/time/@datetime[1]').extract_first()
        category = response.xpath('.//div[contains(@class, "caas-logo")]/a/img/@alt[1]').extract_first()
        body = response.xpath('.//div[@class="caas-body"]/p/text()').getall()
        author = response.xpath('.//div[contains(@class, "caas-attr-item-author")]/span/text()').extract_first()
        
        data_extended['date'] = str(date).replace('T',' ').replace('Z','')
        if author:
            data_extended['author'] = author
        else:
            data_extended['author'] = ''

        data_extended['link_author'] = ''
        data_extended['category'] = category
        data_extended['language'] = language

        for i,d in enumerate(body[:5]):
            body[i] = re.sub('(<([^>]+)>)', '', d)

        data_extended['news_body'] = body[:5]
        yield data_extended

    def open_page(self, response): #Funcion para hacer pruebas
        print("texto",response.text)
        open_in_browser(response)