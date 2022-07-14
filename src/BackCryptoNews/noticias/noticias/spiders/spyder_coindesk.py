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
from scrapy.exceptions import CloseSpider
import re
import requests

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

class coindesk(scrapy.Spider):
    name = 'coindesk'
    base_url = 'https://www.coindesk.com'
    counter = 0
    #custom_settings = {'LOG_LEVEL': 'INFO'}        # funciona para visualizar los items scrapeando
    last_new = Last_New(base_url)
    flag = False
    
    headers = {
        "authority": "www.coindesk.com",
        "accept": "*/*",
        "accept-language": "es-419,es;q=0.9",
        "cache-control": "max-age=0",
        "cookie": "AKA_A2=A",
        "if-modified-since": "1657204876267",
        "referer": "https://www.coindesk.com/markets/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }


    def __init__(self, *args, **kwargs):
        self.schedule = kwargs.pop('schedule', '')  # path to where all workflows are stored
        #print("self.schedule",self.schedule)
        
    def start_requests(self):
        url = "https://www.coindesk.com/"
        yield Request(url=url, callback=self.start_search, dont_filter=True)
    
    def start_search(self, response):
        url = "https://www.coindesk.com/pf/api/v3/content/fetch/content-search?query=%7B%22format%22%3A%22article-timeline%22%2C%22from%22%3A{}%2C%22isLiveWirePage%22%3Atrue%2C%22section%22%3A%22%2Fmarkets%22%2C%22sections%22%3A%22%2Fmarkets%22%2C%22size%22%3A6%2C%22sort%22%3A%22display_date%3Adesc%22%2C%22types%22%3A%22%22%7D&d=176&_website=coindesk".format(self.counter)
        querystring = '{"query":"{"format":"article-timeline","from":'
        querystring += str(self.counter)
        querystring += ',"isLiveWirePage":true,"section":"/markets","sections":"/markets","size":6,"sort":"display_date:desc","types":""}","d":"176","_website":"coindesk"}'
        payload = ""
        response = requests.request("GET", url, data=payload, headers=self.headers, params=querystring)
        data = response.json()
        cursos = data['content_elements']

        for curso in cursos:
            link = 'https://www.coindesk.com/'+curso['website_url']
            # Verifica si ultimo se encuentra en la raspada
            if link == self.last_new:
                print("ultimoScrapy",link)
                self.flag = True

            # Guardar los datos
            item = NoticiasItem()
            item['date'] = str(curso['created_date']).replace('T',' ').replace('Z','').replace(': ',':')
            item['title'] = str(curso['headlines']['basic'])
            item['description'] = curso['subheadlines']['basic']
            item['link'] = link
            item['category'] = curso['taxonomy']['primary_section']['name']
            item['author'] = curso['credits']['by'][0]['name']
            item['image'] = curso['promo_items']['basic']['additional_properties']['originalUrl']
            item['link_author'] = 'https://www.coindesk.com/author/'+ curso['credits']['by'][0]['_id']
            item['dominio'] = self.base_url
            item['language'] = 'en-US'
            item['views'] = 0
            item['history'] = str(self.schedule)

            if link is not None:
                yield scrapy.Request(url=link, callback = self.parse_information, meta={'same_item':item})
            
            else:
                yield item

        # Verifica si encontro la ultima noticia en esa pagina
        if self.flag:
            raise CloseSpider('Encontro la ultima scrapy')

        # Paginacion
        self.counter += 6
        yield Request(url='https://www.coindesk.com/', callback=self.start_search, dont_filter=True)

    def parse_information(self, response):
        data_extended = response.meta.get('same_item')
        body = response.xpath('//div[contains(@class, "contentstyle__StyledWrapper-g5cdrh-0 gCDWPA")]/div/div/p').getall()
        for i,d in enumerate(body[:5]):
            body[i] = re.sub('(<([^>]+)>)', '', d)
        data_extended['news_body'] = body[:5]
        yield data_extended

    def open_page(self, response): #Funcion para hacer pruebas
        print("texto",response.text)
        open_in_browser(response)