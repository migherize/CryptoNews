import subprocess
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Para compilar cada projecto de araña
while True:
    # Hora de Italia
    today = datetime.now(ZoneInfo("Europe/Berlin"))
    dt_string = today.strftime("%d/%m/%Y %H:%M:%S")
    
    # Fecha y hora de actualizacion
    schedule = "schedule={}".format(dt_string)

    # Llamada a cada pagina de noticias
    subprocess.call(["scrapy","crawl","cryptonomist","-a",schedule],cwd="./noticias")
    #subprocess.call(["scrapy","crawl","araña","-a",schedule],cwd="./noticias")

    print("ESPERANDO SIGUIENTE HORA")
    time.sleep(60)