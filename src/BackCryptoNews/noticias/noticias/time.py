
import string
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def time(date):
    date = date.lower()
    today = datetime.now(ZoneInfo("Europe/Berlin"))
    
    letter = re.findall(r'^[a-z]+',date)
    day = re.findall(r'days ago|day ago',date)
    horas = re.findall(r'hours|hour',date)
    min = re.findall(r'min|minute|minutes',date)
    
    if letter:
        num = re.findall(r'[0-9]+,',date)
        nombre = re.findall(r'^[a-z]+',date)
        ano = re.findall(r'[0-9]+$',date)
        s = "{} {}".format(num[0].replace(',',''),nombre[0])
        pubilicada = datetime.strptime("{} {}".format(s,ano[0]), "%d %b %Y").strftime("%Y-%m-%d")
        date = str(pubilicada)
    
    elif day:
        num = re.findall(r'^[0-9]+',date)
        if num:
            pubilicada = today - timedelta(days = int(num[0]))
            date = str(pubilicada)
    
    elif horas:
        hora = re.findall(r'^[0-9]+',date)
        if hora:
            pubilicada = today - timedelta(hours = int(hora[0]))
            date = str(pubilicada)
    elif min:
        hora = re.findall(r'^[0-9]+',date)
        if hora:
            pubilicada = today - timedelta(minutes = int(hora[0]))
            date = str(pubilicada)
    else:
        print("ningun cambio")

    return date
    
    
#date = "Apr 17, 2022"
#date = "2 day ago"
#date = "2 hours ago"
#date = "2 min"
date = "16 Jun 2022"
organizar_date = date.split()
organizar_date[0] = organizar_date[0] + ','
date = organizar_date[1] +' '+ organizar_date[0] +' '+organizar_date[2]
print("date",date)

trans_data = time(date)
print("trans_data",trans_data)

