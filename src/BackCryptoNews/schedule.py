import subprocess
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

#import sys
#sys.path.append('/Users/migherize/Sourcetree/NewCrypto/noticias/') # Adds higher directory to python modules path.

# Para compilar cada projecto de araña
while True:
    # Hora de Italia
    today = datetime.now(ZoneInfo("Europe/Berlin"))
    dt_string = today.strftime("%d/%m/%Y %H:%M:%S")
    
    # Fecha y hora de actualizacion
    schedule = "schedule={}".format(dt_string)

    # Llamada a cada pagina de noticias
    #subprocess.call(["scrapy","crawl","cryptonomist","-a",schedule],cwd="./noticias")
    #subprocess.call(["scrapy","crawl","criptovaluta","-a",schedule],cwd="./noticias")
    #subprocess.call(["scrapy","crawl","watcher_guru","-a",schedule],cwd="./noticias")
    #subprocess.call(["scrapy","crawl","coinmarketcap","-a",schedule],cwd="./noticias")
    subprocess.call(["scrapy","crawl","coindesk","-a",schedule],cwd="./noticias")
    #subprocess.call(["scrapy","crawl","yahoo","-a",schedule],cwd="./noticias")
    
    # Volver a llamarse
    print("ESPERANDO SIGUIENTE HORA")
    time.sleep(3600)    