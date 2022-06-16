# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
import json
import os
from os import path
import sqlite3

# constants
data = {}
path_folder = (os.getcwd()).replace('BackCryptoNews/noticias','') + 'data/'
name = 'items'
workname = name + '.json'
list_item = ['date','title','description','link','history','language','category','image']
name_db = '{}_history.db'.format(name)

# Conexion SQL
con = sqlite3.connect(path.join(path_folder, name_db))
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS info (history text, title text, descripcion text, link text, date_news text, language text, category text, image text)''')

class NoticiasPipeline:
    def open_spider(self, spider):
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
                # insertar a DB
                with open(path.join(path_folder, workname)) as file:
                    data_json = json.load(file)
                
                # separar cada dato en cada columna de la DB e insertar
                for lista in data_json:
                    for key,value in lista.items():
                        if key == list_item[0]:
                            date_news = value
                            
                        elif key == list_item[1]:
                            titulo = value
                            
                        elif key == list_item[2]:
                            descripcion = value
                            
                        elif key == list_item[3]:
                            link = value
                            
                        elif key == list_item[4]:
                            historial = value
                        
                        elif key == list_item[5]:
                            language = value
                        
                        elif key == list_item[6]:
                            category = value
                        
                        elif key == list_item[7]:
                            image = value

                    param = (historial,titulo,descripcion,link,date_news,language,category,image)
                    cur.execute("INSERT INTO info VALUES (?,?,?,?,?,?,?,?)",param)
                    con.commit()
                con.close()
                
                #Escribir json noticias
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
        