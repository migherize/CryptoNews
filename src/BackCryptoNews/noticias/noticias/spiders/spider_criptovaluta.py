# -*- coding: utf-8 -*-
import scrapy
import json 
from datetime import datetime
from scrapy import Request
from scrapy.utils.response import open_in_browser
from noticias.items import NoticiasItem
from noticias.Time_format import time_format
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

class criptovaluta(scrapy.Spider):
    name = 'criptovaluta'
    base_url = 'https://www.criptovaluta.it'
    last_new = Last_New(base_url)
    #custom_settings = {'LOG_LEVEL': 'INFO'}     # funciona para visualizar los items scrapeando
    
    # Aux
    page = 0
    flag = False

    def __init__(self, *args, **kwargs):
        self.schedule = kwargs.pop('schedule', '')  # path to where all workflows are stored
        
    def start_requests(self):
        url = 'https://www.criptovaluta.it/news'
        print("last_new",self.last_new)
        yield Request(url=url, callback=self.start_search, dont_filter=True)
    
    def start_search(self, response):
        self.page += 1 
        print("pagina:", self.page)
        if self.page == 1:
            news = response.xpath('//div[contains(@class, "post-listing archive-box")]/article')
        else:
            news = response.xpath("//article[contains(@class, 'item-list')]")

        for n in news:
            fecha = n.xpath('.//p[contains(@class, "post-meta")]').extract_first()
            title = n.xpath('.//h2/a/text()').extract_first()
            descripcion = n.xpath('.//div[contains(@class, "entry")]/p/text()').extract_first()
            link = n.xpath('.//div[contains(@class, "entry")]/a/@href').extract_first()
            link_image = n.xpath('.//div[contains(@class, "post-thumbnail")]/a/img/@data-lazy-srcset').extract_first()
            author = n.xpath('.//p/span[contains(@class, "post-meta-author")]/a/text()').extract_first()
            link_author = n.xpath('.//p/span[contains(@class, "post-meta-author")]/a/@href').extract_first()

            # Guardar los datos
            if link == self.last_new:
                print("ultimoScrapy",link)
                self.flag = True
           
            item = NoticiasItem()
            
            #Convierte la fecha en formato YYYY-MM-DD
            date_new = re.findall(r'[0-9]{2}\/[0-9]{2}\/[0-9]{2}\s[0-9]{2}:[0-9]{2}',fecha)
            split_date = date_new[0].split()
            d = split_date[0].replace('/','-')
            split_digito = d.split('-')
            date = datetime(int('20'+split_digito[2]), int(split_digito[1]), int(split_digito[0]))
            item['date'] = date

            item['title'] = title
            item['description'] = descripcion
            item['link'] = link
            item['history'] = str(self.schedule)
            
            # transformacion de link imagen
            print("link_image",link_image)
            link_image = re.findall(r'^https((?:\S?)+)',link_image)
            print("Nuevo link_image",link_image)

            item['image'] = 'https'+link_image[0]
            item['author'] = author
            item['link_author'] = link_author
            item['dominio'] = self.base_url
                
            # News Body
            if link is not None:
                yield scrapy.Request(url=link, callback = self.parse_information, meta={'same_item':item})

            else:
                language = response.xpath('/html/@lang').extract_first()
                item['language'] = language
                item['category'] = 'Crypto'
                item['news_body'] = ''
                yield item
            
        # Verifica si encontro la ultima noticia en esa pagina
        if self.flag:
            raise CloseSpider('Encontro la ultima scrapy')

        # Paginacion
        url1 = "https://www.criptovaluta.it/wp-admin/admin-ajax.php"
        for w in range(2,10):
            payload = "page={}&action=ajax_script_load_more&category=news".format(w)
            headers = {
                "authority": "www.criptovaluta.it",
                "accept": "*/*",
                "accept-language": "es-ES,es;q=0.9",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "cookie": "_gcl_au=1.1.398167544.1656809232; _ga=GA1.2.804106031.1656809239; _gid=GA1.2.750874388.1656809239; CookieConsent=^{stamp:^%^27QlHZmsbaq5KLc6l9i64XnWf2RZ4gopdGTD6sq2De6+LbRKFaR8RSJw==^%^27^%^2Cnecessary:true^%^2Cpreferences:true^%^2Cstatistics:true^%^2Cmarketing:true^%^2Cver:2^%^2Cutc:1656809301833^%^2Cregion:^%^27ve^%^27^}; _gat_UA-99986318-1=1; _gali=loadMore",
                "origin": "https://www.criptovaluta.it",
                "referer": "https://www.criptovaluta.it/news",
                "sec-ch-ua": "^\^.Not/A",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "^\^Windows^^",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
                "x-requested-with": "XMLHttpRequest"
            }
            yield scrapy.Request(url=url1, method='POST',callback = self.start_search, body=payload, headers=headers)


    def parse_information(self, response):
        # Lectura de el item
        data_extended = response.meta.get('same_item')
        # Recoleccion
        #category = response.xpath('//div[contains(@class, "content")]/span[contains(@class, "category")]/text()').extract_first()
        language = response.xpath('/html/@lang').extract_first()
        body = response.xpath('//div[contains(@class, "entry")]/p').getall()
        
        # Limpiar HTML
        for i,d in enumerate(body[:5]):
            body[i] = re.sub('(<([^>]+)>)', '', d)
        data_extended['news_body'] = body[:5]

        # Guardar
        data_extended['category'] = 'Crypto'
        data_extended['language'] = language
        data_extended['news_body'] = body[:3]
        yield data_extended

    def open_page(self, response): #Funcion para hacer pruebas
        print("texto",response.text)
        open_in_browser(response)