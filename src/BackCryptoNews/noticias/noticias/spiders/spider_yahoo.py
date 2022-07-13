import scrapy
import string
import json 
from datetime import date, datetime
from scrapy import Request
from scrapy.utils.response import open_in_browser
from noticias.items import NoticiasItem
from noticias.Time_format import time_format
from scrapy import Selector
from googletrans import Translator
import re

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


class yahoo(scrapy.Spider):
    name = 'yahoo'
    base_url = 'https://finance.yahoo.com'
    contador = 0
    #custom_settings = {'LOG_LEVEL': 'INFO'}        # funciona para visualizar los items scrapeando

    def _init_(self, *args, **kwargs):
        self.schedule = kwargs.pop('schedule', '')  # path to where all workflows are stored
        #print("self.schedule",self.schedule)
        
    def start_requests(self):
        urls = ['https://finance.yahoo.com/topic/crypto/']
        print('********************',urls)
        for url in urls:
            yield Request(url=url, callback=self.start_search, dont_filter=True)
            

    def start_url(self,response):
        print("url",response.url)
        if self.contador < 3:
            yield Request(url=response.url, callback=self.start_search, dont_filter=True)

    def start_search(self, response):
        print("url***************************",response.url)
        news = response.xpath('//div[@id="Fin-Stream"]/ul[@class="My(0) P(0) Wow(bw) Ov(h)"]/li[contains(@class, "Pos(r)")]')
        print("noticas",len(news))
        
        for n in news:
            title = n.xpath('.//h3[contains(@class, "Mb(5px)")]/a/text()').extract_first()
            descripcion = n.xpath('.//p[@class="Fz(14px) Lh(19px) Fz(13px)--sm1024 Lh(17px)--sm1024 LineClamp(2,38px) LineClamp(2,34px)--sm1024 M(0)"]/text()').extract_first()
            link = n.xpath('.//div[@class="Ov(h) Pend(44px) Pstart(25px)"]/h3/a/@href').extract_first()
            link_image = n.xpath('.//div[@class="H(0) Ov(h) Bdrs(2px)"]/img/@src').extract_first()
            author = n.xpath('.//div[@class="C(#959595) Fz(11px) D(ib) Mb(6px)"]/span[1]/text()').extract_first()
            #link_author = n.xpath('.//p[contains(@class, "author")]/a/@href').extract_first()


            #print("date",date)
            #if fecha:

            # convertir la fecha en ingles
                #date = Translator().translate(str(fecha.replace('-','').replace('Lug','Jul'))).text
                #organizar_date = date.split()
                #organizar_date[0] = organizar_date[0] + ','
                #date = organizar_date[1] +' '+ organizar_date[0] +' '+organizar_date[2]
            #else:
                #print()


            # Guardar los datos
            item = NoticiasItem()
            #date = time_format(date.strip())
            item['title'] = title
            item['description'] = descripcion
            item['link'] = self.base_url + str(link)
            item['history'] = str(self.schedule)
            item['image'] = link_image
            item['author'] = author
            #item['link_author'] = link_author
            item['dominio'] = self.base_url
            item['views'] = 0
            
            # News Body
            if link is not None:
                yield scrapy.Request(url= self.base_url + link, callback = self.parse_information, meta={'same_item':item})

            else:
                language = response.xpath('/html/@lang').extract_first()
                item['language'] = language
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
        date = response.xpath('//div[contains(@class, "caas-attr-time-style")]/time/@datetime[1]').extract_first()
        category = response.xpath('.//div[contains(@class, "caas-logo")]/a/img/@alt[1]').extract_first()
        data_extended['date'] = str(date).replace('T','').replace('Z','')
        data_extended['category'] = category
        body = response.xpath('//div[@class="caas-body"]/p/text()').getall()
        data_extended['language'] = language
        for i,d in enumerate(body[:5]):
            body[i] = re.sub('(<([^>]+)>)', '', d)
            print("list_body[i]",body[i])
        data_extended['news_body'] = body[:5]
        yield data_extended

    def open_page(self, response): #Funcion para hacer pruebas
        print("texto",response.text)
        open_in_browser(response)