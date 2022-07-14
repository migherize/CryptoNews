from email import header
from unicodedata import category
from wsgiref import headers
import scrapy
import string
from scrapy import Request
from scrapy.utils.response import open_in_browser
from noticias.items import NoticiasItem
from noticias.Time_format import time_format
from scrapy.exceptions import CloseSpider
import re
import json


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


class coinmarketcap(scrapy.Spider):
    name = 'coinmarketcap'
    base_url = 'https://coinmarketcap.com'
    last_new = Last_New(base_url)
    flag = False
    #custom_settings = {'LOG_LEVEL': 'INFO'}     # funciona para visualizar los items scrapeando
    header={
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }
    
    def __init__(self, *args, **kwargs):
        self.schedule = kwargs.pop('schedule', '')  # path to where all workflows are stored
        
    def start_requests(self):
        url = 'https://coinmarketcap.com/alexandria/categories/market-musing'
        print("last_new",self.last_new)
        yield Request(url=url, callback=self.start_search, dont_filter=True, headers=self.header)

    def start_search(self, response):
        data = response.xpath('//*[contains(@id, "NEXT_DATA")]/text()').get()
        res = json.loads(data)
        info = res['props']['pageProps']['response']['pages']['data']
        for i in info:
            link = 'https://coinmarketcap.com/alexandria/article/' + str(i['slug'])
            
            # Verifica si ultimo se encuentra en la raspada
            if link == self.last_new:
                print("ultimoScrapy",link)
                self.flag = True

            # Guardar los datos
            item = NoticiasItem()
            item['title'] = str(i['title'])
            item['category'] = i['categories'][0]['title']
            item['author']= i['author']['name']
            item['date'] = str(i['created_at']).replace('T',' ').replace('Z','').replace(': ',':')
            item['description'] = i['meta']
            item['link'] = link
            item['image'] = 'https://academy-public.coinmarketcap.com/' + i['image']['thumbnail']
            item['dominio'] = self.base_url
            item['views'] = 0
            item['link_author'] = ''
            item['history'] = str(self.schedule)
            if 'en' in str(i['language']):
                item['language'] = 'en-US'
            else:
                item['language'] = i['language']

            if link is not None:
                yield scrapy.Request(url=link, callback = self.parse_information, meta={'same_item':item},headers=self.header)
            
            else:
                yield item
    
        # Verifica si encontro la ultima noticia en esa pagina
        if self.flag:
            raise CloseSpider('Encontro la ultima scrapy')

        # Paginacion
        next_url = response.xpath('//ul[contains(@class, "MuiPagination-ul")]/li/a').getall()
        for next in next_url:
            next_to = re.findall(r'Go\sto\snext\spage',next)
            if next_to:
                link_to = re.findall(r'href="((?:\S?)+)"',next)
                if link_to:
                    next_page = 'https://coinmarketcap.com/alexandria' + link_to[0].replace('href=','').replace('"','')
                    print("next_page",next_page)
                    yield Request(url=next_page, callback=self.start_search, dont_filter=True, headers=self.header)

    def parse_information(self, response):
        data_extended = response.meta.get('same_item')
        body = response.xpath('//article[contains(@class, "ArticleContent")]/p').getall()
        for i,d in enumerate(body[:5]):
            body[i] = re.sub('(<([^>]+)>)', '', d)
        data_extended['news_body'] = body[:5]
        yield data_extended

    def open_page(self, response): #Funcion para hacer pruebas
        print("texto",response.text)
        open_in_browser(response)
