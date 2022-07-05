# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from email.mime import base
import json
import os
import scrapy
from scrapy.exceptions import CloseSpider
from os import path
import sqlite3

# constants
data = {}

# Mac o Linux
path_folder = (os.getcwd()).replace('BackCryptoNews/noticias','') + 'data/'

# Windows
# path_folder = (os.getcwd()).replace('\\BackCryptoNews\\noticias','') + '\\data/'

name = 'items'
workname = name + '.json'
list_item = ['date','title','description','link','history','image','author','link_author','dominio','category','language','news_body']

base_url = ['cryptonomist.ch','criptovaluta.it','watcher.guru','en.cryptonomist.ch','coinmarketcap.com']

class NoticiasPipeline:
    def open_spider(self, spider):
        '''
        last_new = []
        # Leer la ultima scrapiada
        if os.path.exists(path.join(path_folder, workname)):
            with open(path.join(path_folder, workname)) as file:
                data_json = json.load(file)

            # Buscar el ultima noticia scrapiada en cada dominio
            for b in base_url:
                bandera = True
                for lista in data_json:
                    for key,value in lista.items():
                        if key == 'link':
                            if bandera and (b in value):
                                print("link",value)
                                last_new.append(value)
                                bandera = False
        
            print("last_new",last_new)
        '''
        self.items = []

    def process_item(self, item, spider):
        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        # Busca el JSON de la ultima raspada (hace 1hr)
        if os.path.exists(path.join(path_folder, workname)):
            with open(path.join(path_folder, workname)) as file:
                data = json.load(file)
            
            #print("schedule", data[0]['history'])
            #print("item", self.items[0]['history'])
            
            if data[0]['history'] == self.items[0]['history']:
                if len(data) > 0:
                    for i in self.items:
                        data.append(i)
                
                print("Tamaño ahora",len(data))            
                # Ordenar los datos raspados
                ordenado = sorted(data, key=lambda x: x["date"], reverse=True)
                with open(path.join(path_folder, workname), 'w') as file:
                    json.dump(ordenado, file, indent=4)
            else:
                if os.path.exists(path.join(path_folder, 'items_history.json')):
                    # Lectura del Json schedule
                    with open(path.join(path_folder, 'items_history.json')) as file:
                        data_json_history = json.load(file)
                else:
                    data_json_history = []

                # Lectura del Json history
                with open(path.join(path_folder, workname)) as file:
                    data_json = json.load(file)
                
                data_json_history+=data_json
                
                file = open(path.join(path_folder, 'items_history.json'), 'w')
                file.write(json.dumps(data_json_history, indent=4))
                file.close()  

                #Escribir json noticias nuevas
                write_json(self.items)
        else:
            #Escribir json noticias
            write_json(self.items)
        

def write_json(items):
    item = []

    if len(items) > 0:
        for i in items:
            item.append(i)
        ordenado = sorted(item, key=lambda x: x["date"], reverse=True)
    
    file = open(path.join(path_folder, workname), 'w')
    file.write(json.dumps(ordenado, indent=4))
    file.close()  
        